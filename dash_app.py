import dash
from dash import dcc, html, Input, Output, State, ctx, callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import requests
import time
import os
import base64
import io
from pathlib import Path
import tempfile
from dotenv import load_dotenv
from params import DEFAULT_FEW_SHOT_EXAMPLES

# Load environment variables
load_dotenv()

# API URL configuration
# In local development: use localhost
# In production: use the Cloud Run URL
# Set DEPLOYMENT_ENV=production in your environment variables
is_production = os.getenv("DEPLOYMENT_ENV") == "production"
API_URL = os.getenv("API_URL", "https://insightgen-api-195411721870.us-central1.run.app" if is_production else "http://localhost:8080")

# Log the API URL being used (helpful for debugging)
print(f"Using API URL: {API_URL}")

# Function to fetch available generators
def fetch_generators():
    try:
        response = requests.get(f"{API_URL}/generators/")
        if response.status_code == 200:
            # Extract the generators list from the response
            response_data = response.json()
            return response_data.get("generators", [])
        else:
            print(f"Failed to fetch generators: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching generators: {str(e)}")
        return []

# Initialize the Dash app with Bootstrap styling
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)
server = app.server

# App title
app.title = "InsightGen: AI-Powered Insights"

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("InsightGen: AI-Powered Insights", className="mt-4 mb-3"),
            html.P(
                "Generate insightful headlines for your market research presentations. "
                "Currently supporting BGS studies only. "
                "Upload your PPTX and PDF files, provide some context, and let AI do the rest!",
                className="lead mb-4"
            ),
        ], width=12)
    ]),

    # File upload section
    dbc.Card([
        dbc.CardHeader("Upload Files"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.P("Upload PPTX file"),
                    dcc.Upload(
                        id='upload-pptx',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select PPTX File')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        multiple=False
                    ),
                    html.Div(id='pptx-upload-output')
                ], width=6),
                dbc.Col([
                    html.P("Upload PDF file"),
                    dcc.Upload(
                        id='upload-pdf',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select PDF File')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        multiple=False
                    ),
                    html.Div(id='pdf-upload-output')
                ], width=6)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Submit", id="inspect-button", color="primary", className="mt-3", n_clicks=0)
                ], width=12, className="text-center")
            ])
        ])
    ], className="mb-4"),

    # Inspection results section
    html.Div(id="inspection-results-container", style={"display": "none"}),

    # Processing form section
    html.Div(id="processing-form-container", style={"display": "none"}),

    # Results section
    html.Div(id="results-container"),

    # Processing status section - Always in layout but hidden initially
    html.Div([
        html.H4("Processing Status", className="mt-4"),
        dbc.Progress(id="progress-bar", value=0, className="mb-3"),
        html.Div(id="status-text")
    ], id="processing-status-container", style={"display": "none"}),

    # Store components for file data and state
    dcc.Store(id='pptx-store'),
    dcc.Store(id='pdf-store'),
    dcc.Store(id='inspection-results-store'),
    dcc.Store(id='job-id-store'),
    dcc.Store(id='processing-completed', data=False),

    # Interval for polling job status
    dcc.Interval(
        id='job-status-interval',
        interval=1000,  # 1 second
        n_intervals=0,
        disabled=True
    ),

    # Sidebar information
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("About InsightGen"),
                dbc.CardBody([
                    html.P("InsightGen uses vision and language AI to analyze market research reports "
                           "and generate insightful headlines and observations."),
                    html.P("Version: 0.1.0"),
                    html.P("Developed by: Sumit Kamra"),

                    html.H5("Instructions", className="mt-3"),
                    html.Ul([
                        html.Li("Currently only supports BGS studies"),
                        html.Li("Ensure PPTX has not hidden slides PDF is identical to PPTX"),
                        html.Li("Ensure header slides layout start with \"HEADER\""),
                        html.Li("Ensure client brands, competitors, market, etc. are mentioned in the prompt"),
                        html.Li("Add any additional user instructions can be added in the prompt")
                    ]),

                    html.H5("API Status", className="mt-3"),
                    html.Div(id="api-status")
                ])
            ])
        ], width=12, className="mt-4")
    ])
], fluid=True)

# Callback to handle PPTX file upload
@callback(
    Output('pptx-store', 'data'),
    Output('pptx-upload-output', 'children'),
    Input('upload-pptx', 'contents'),
    State('upload-pptx', 'filename'),
    prevent_initial_call=True
)
def store_pptx(contents, filename):
    if contents is None:
        raise PreventUpdate

    content_type, content_string = contents.split(',')

    return {
        'content': content_string,
        'filename': filename
    }, html.Div([
        html.I(className="fas fa-check-circle text-success me-2"),
        f"Uploaded: {filename}"
    ])

# Callback to handle PDF file upload
@callback(
    Output('pdf-store', 'data'),
    Output('pdf-upload-output', 'children'),
    Input('upload-pdf', 'contents'),
    State('upload-pdf', 'filename'),
    prevent_initial_call=True
)
def store_pdf(contents, filename):
    if contents is None:
        raise PreventUpdate

    content_type, content_string = contents.split(',')

    return {
        'content': content_string,
        'filename': filename
    }, html.Div([
        html.I(className="fas fa-check-circle text-success me-2"),
        f"Uploaded: {filename}"
    ])

# Callback to check API status
@callback(
    Output('api-status', 'children'),
    Input('inspect-button', 'n_clicks'),
    Input('job-status-interval', 'n_intervals')
)
def check_api_status(n_clicks, n_intervals):
    try:
        api_response = requests.get(f"{API_URL}/")
        if api_response.status_code == 200:
            return html.Div([
                html.I(className="fas fa-check-circle text-success me-2"),
                f"API is online (v{api_response.json().get('version', 'unknown')})"
            ])
        else:
            return html.Div([
                html.I(className="fas fa-times-circle text-danger me-2"),
                "API is not responding correctly"
            ])
    except:
        return html.Div([
            html.I(className="fas fa-times-circle text-danger me-2"),
            "Cannot connect to API"
        ])

# Callback to inspect files
@callback(
    Output('inspection-results-store', 'data'),
    Output('inspection-results-container', 'children'),
    Output('inspection-results-container', 'style'),
    Input('inspect-button', 'n_clicks'),
    State('pptx-store', 'data'),
    State('pdf-store', 'data'),
    prevent_initial_call=True
)
def inspect_files(n_clicks, pptx_data, pdf_data):
    if n_clicks == 0 or pptx_data is None or pdf_data is None:
        raise PreventUpdate

    # Create loading spinner
    loading = dbc.Spinner(html.Div("Inspecting files..."), color="primary")

    # Prepare files for inspection
    try:
        pptx_content = base64.b64decode(pptx_data['content'])
        pdf_content = base64.b64decode(pdf_data['content'])

        files = {
            "pptx_file": (pptx_data['filename'], pptx_content, "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
            "pdf_file": (pdf_data['filename'], pdf_content, "application/pdf"),
        }

        # Call the inspect-files endpoint
        response = requests.post(f"{API_URL}/inspect-files/", files=files)

        # Check for HTTP errors
        if response.status_code >= 400:
            error_detail = response.json().get("detail", "Unknown error")
            return None, dbc.Alert(f"Error during inspection: {error_detail}", color="danger"), {"display": "block"}

        # Process successful response
        inspection_results = response.json()

        # Create results display
        results_display = []

        # Display warnings
        if inspection_results["warnings"]:
            results_display.append(html.H4("⚠️ Warnings", className="mt-3"))
            for warning in inspection_results["warnings"]:
                results_display.append(dbc.Alert(warning, color="warning"))

        # Display slide statistics
        if "slide_stats" in inspection_results and inspection_results["slide_stats"]:
            stats = inspection_results["slide_stats"]

            results_display.append(html.H4("📊 Inspection Results", className="mt-4"))

            # Total slides
            results_display.append(html.P(f"Total Slides: {stats['total_slides']}", className="fw-bold"))

            # Header slides
            header_count = stats["header_slides"]["count"]
            if header_count > 0:
                results_display.append(html.P([
                    "✅ Header Slides: ",
                    html.Span(f"{header_count} slides", className="fw-bold"),
                    " (no headlines will be generated for these)"
                ]))

                results_display.append(dbc.Card([
                    dbc.CardHeader("View header slide numbers"),
                    dbc.CardBody(
                        f"Slide numbers: {', '.join(map(str, stats['header_slides']['slide_numbers']))}"
                    )
                ], className="mb-3"))
            else:
                results_display.append(html.P([
                    "⚠️ Header Slides: ",
                    html.Span("0 slides", className="fw-bold"),
                    " (no header slides detected)"
                ]))
                results_display.append(html.P(
                    "Consider defining header slides in your presentation by using layouts with names starting with 'HEADER'",
                    className="fst-italic"
                ))

            # Content slides
            content_count = stats["content_slides"]["count"]
            results_display.append(html.P([
                "📝 Content Slides: ",
                html.Span(f"{content_count} slides", className="fw-bold"),
                " (headlines will be generated for these)"
            ]))

            # Missing placeholders
            missing_count = stats["missing_placeholders"]["count"]
            if missing_count == 0:
                results_display.append(html.P([
                    "✅ Title Placeholders: ",
                    html.Span("All content slides have title placeholders", className="fw-bold")
                ]))
            else:
                results_display.append(html.P([
                    "❌ Title Placeholders: ",
                    html.Span(f"{missing_count} content slides are missing title placeholders", className="fw-bold")
                ]))

                results_display.append(dbc.Card([
                    dbc.CardHeader("View slides missing title placeholders"),
                    dbc.CardBody(
                        f"Slide numbers: {', '.join(map(str, stats['missing_placeholders']['slide_numbers']))}"
                    )
                ], className="mb-3"))

                results_display.append(html.P(
                    "Headlines cannot be inserted into slides without title placeholders",
                    className="fst-italic"
                ))

        return inspection_results, dbc.Card([
            dbc.CardHeader("Inspection Results"),
            dbc.CardBody(results_display)
        ]), {"display": "block"}

    except requests.RequestException as e:
        return None, dbc.Alert(f"Error connecting to API: {str(e)}", color="danger"), {"display": "block"}
    except Exception as e:
        return None, dbc.Alert(f"Error: {str(e)}", color="danger"), {"display": "block"}

# Callback to show processing form if inspection is valid
@callback(
    Output('processing-form-container', 'children'),
    Output('processing-form-container', 'style'),
    Input('inspection-results-store', 'data'),
    prevent_initial_call=True
)
def show_processing_form(inspection_results):
    if inspection_results is None or not inspection_results.get("is_valid", False):
        raise PreventUpdate

    # Fetch available generators
    generators = fetch_generators()

    # Create generator options
    generator_options = {g["name"]: g["id"] for g in generators} if generators else {"Brand Growth Study (Default)": "bgs_default"}
    generator_names = list(generator_options.keys())

    # Create the processing form
    form = dbc.Card([
        dbc.CardHeader("Generate Insights"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Select Generator"),
                    dcc.Dropdown(
                        id="generator-dropdown",
                        options=[{"label": name, "value": generator_options[name]} for name in generator_names],
                        value=generator_options[generator_names[0]],
                        clearable=False
                    ),
                    dbc.Tooltip(
                        "Choose the type of analysis to perform",
                        target="generator-dropdown"
                    )
                ], width=12, className="mb-3")
            ]),

            dbc.Row([
                dbc.Col([
                    html.Label("Prompt: Market, Brand Context and Additional Instructions"),
                    dbc.Textarea(
                        id="user-prompt",
                        value="""Market: Vietnam;
Client brands: Heineken, Tiger, Bia Viet, Larue, Bivina;
Competitors: 333, Saigon Beer, Hanoi Beer;
Additional instructions: """,
                        style={"height": "130px"}
                    )
                ], width=12, className="mb-3")
            ]),

            dbc.Row([
                dbc.Col([
                    html.Label("Slide Memory"),
                    dcc.Slider(
                        id="context-window-size",
                        min=0,
                        max=50,
                        step=1,
                        value=20,
                        marks={i: str(i) for i in range(0, 51, 10)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                    dbc.Tooltip(
                        "Number of previous slides to maintain in context",
                        target="context-window-size"
                    )
                ], width=12, className="mb-3")
            ]),

            dbc.Row([
                dbc.Col([
                    html.Label("Custom Examples - Edit or add more examples (Optional)"),
                    dbc.Textarea(
                        id="few-shot-examples",
                        value=DEFAULT_FEW_SHOT_EXAMPLES,
                        style={"height": "150px"}
                    ),
                    dbc.Tooltip(
                        "Provide custom examples to guide the headline generation",
                        target="few-shot-examples"
                    )
                ], width=12, className="mb-3")
            ]),

            dbc.Row([
                dbc.Col([
                    dbc.Button("Submit", id="process-button", color="primary", className="w-100")
                ], width=12)
            ])
        ])
    ])

    return form, {"display": "block"}

# Callback to process files and start job
@callback(
    Output('job-id-store', 'data'),
    Output('job-status-interval', 'disabled'),
    Output('processing-status-container', 'style'),
    Output('progress-bar', 'value'),
    Output('status-text', 'children'),
    Output('results-container', 'children'),
    Input('process-button', 'n_clicks'),
    State('pptx-store', 'data'),
    State('pdf-store', 'data'),
    State('generator-dropdown', 'value'),
    State('user-prompt', 'value'),
    State('context-window-size', 'value'),
    State('few-shot-examples', 'value'),
    prevent_initial_call=True
)
def process_files(n_clicks, pptx_data, pdf_data, generator_id, user_prompt, context_window_size, few_shot_examples):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate

    try:
        # Decode file contents
        pptx_content = base64.b64decode(pptx_data['content'])
        pdf_content = base64.b64decode(pdf_data['content'])

        # Prepare files for upload
        files = {
            "pptx_file": (pptx_data['filename'], pptx_content, "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
            "pdf_file": (pdf_data['filename'], pdf_content, "application/pdf"),
        }

        # Prepare form data
        data = {
            "user_prompt": user_prompt,
            "context_window_size": str(context_window_size),
            "generator_id": generator_id,
        }

        if few_shot_examples:
            data["few_shot_examples"] = few_shot_examples

        # Submit job
        response = requests.post(f"{API_URL}/upload-and-process/", files=files, data=data)

        # Check for HTTP errors
        if response.status_code >= 400:
            error_detail = response.json().get("detail", "Unknown error")

            # Handle specific validation errors
            if "Slide count mismatch" in error_detail:
                return None, True, {"display": "none"}, 0, None, dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    f"{error_detail}",
                    html.P("Please ensure both files have the same number of slides before proceeding.", className="mt-2")
                ], color="danger")
            elif "Unsupported or corrupt" in error_detail or "Invalid or corrupt" in error_detail:
                return None, True, {"display": "none"}, 0, None, dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    f"{error_detail}",
                    html.P("Please check your files and try again with valid formats.", className="mt-2")
                ], color="danger")
            else:
                return None, True, {"display": "none"}, 0, None, dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    f"Error: {error_detail}"
                ], color="danger")

        # Process successful response
        response_data = response.json()
        job_id = response_data["job_id"]

        # Display any warnings
        warnings_display = []
        if "warnings" in response_data and response_data["warnings"]:
            for warning in response_data["warnings"]:
                if "Filename mismatch" in warning:
                    warnings_display.append(dbc.Alert([
                        html.I(className="fas fa-exclamation-triangle me-2"),
                        f"{warning}",
                        html.P("Processing will continue, but please consider using matching filenames in the future.", className="mt-2")
                    ], color="warning"))

        # Initial status
        status_text = dbc.Alert("Stage 1/4: Slide processing - Preparing slides for analysis...", color="info")

        return job_id, False, {"display": "block"}, 5, status_text, html.Div(warnings_display)

    except requests.RequestException as e:
        return None, True, {"display": "none"}, 0, None, dbc.Alert(f"Error connecting to API: {str(e)}", color="danger")
    except Exception as e:
        return None, True, {"display": "none"}, 0, None, dbc.Alert(f"Error: {str(e)}", color="danger")

# Callback to update job status
@callback(
    Output('progress-bar', 'value', allow_duplicate=True),
    Output('status-text', 'children', allow_duplicate=True),
    Output('processing-completed', 'data'),
    Output('processing-status-container', 'style', allow_duplicate=True),
    Output('results-container', 'children', allow_duplicate=True),
    Input('job-status-interval', 'n_intervals'),
    State('job-id-store', 'data'),
    State('processing-completed', 'data'),
    prevent_initial_call=True
)
def update_job_status(n_intervals, job_id, completed):
    if job_id is None:
        raise PreventUpdate

    if completed:
        # If processing is already completed, don't update anything
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    try:
        status_response = requests.get(f"{API_URL}/job-status/{job_id}")

        if status_response.status_code == 200:
            job_status = status_response.json()
            status = job_status["status"]

            if status == "completed":
                # Create metrics display
                metrics_display = []
                if "metrics" in job_status and job_status["metrics"]:
                    metrics = job_status["metrics"]

                    metrics_display = [
                        html.H4("Performance Metrics", className="mt-4"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("Total Slides"),
                                        html.H3(metrics.get("total_slides", 0))
                                    ])
                                ], className="text-center mb-3")
                            ], width=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("Content Slides Processed"),
                                        html.H3(metrics.get("content_slides_processed", 0))
                                    ])
                                ], className="text-center mb-3")
                            ], width=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("Observations Generated"),
                                        html.H3(metrics.get("observations_generated", 0))
                                    ])
                                ], className="text-center mb-3")
                            ], width=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("Headlines Generated"),
                                        html.H3(metrics.get("headlines_generated", 0))
                                    ])
                                ], className="text-center mb-3")
                            ], width=3)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("Errors"),
                                        html.H3(metrics.get("errors", 0))
                                    ])
                                ], className="text-center mb-3")
                            ], width=4),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("Total Processing Time (s)"),
                                        html.H3(round(metrics.get("total_time_seconds", 0), 2))
                                    ])
                                ], className="text-center mb-3")
                            ], width=4),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H5("Avg. Time per Slide (s)"),
                                        html.H3(round(metrics.get("average_time_per_content_slide", 0), 2))
                                    ])
                                ], className="text-center mb-3")
                            ], width=4)
                        ])
                    ]

                # Create download button
                download_url = f"{API_URL}/download/{job_id}"
                download_filename = job_status.get("output_filename", f"processed_presentation.pptx")

                download_section = [
                    html.H4("Download Results", className="mt-4"),
                    html.A(
                        dbc.Button("Download Processed Presentation", color="success", className="w-100"),
                        href=download_url,
                        download=download_filename,
                        target="_blank"
                    )
                ]

                # Combine all results
                new_results = [
                    dbc.Alert("Processing completed successfully!", color="success"),
                    *metrics_display,
                    *download_section
                ]

                # Hide the progress container when completed
                return 100, dbc.Alert("Processing completed successfully!", color="success"), True, {"display": "none"}, new_results

            elif status == "failed":
                return 100, dbc.Alert(f"Processing failed: {job_status.get('message', 'Unknown error')}", color="danger"), True, {"display": "none"}, dbc.Alert(f"Processing failed: {job_status.get('message', 'Unknown error')}", color="danger")

            else:  # processing
                # Calculate progress based on elapsed time
                elapsed_time = n_intervals  # Each interval is 1 second

                # Update progress based on elapsed time
                if elapsed_time <= 5:
                    # Stage 1: 5% to 20%
                    progress_value = min(5 + (elapsed_time / 5) * 15, 20)
                    status_text = dbc.Alert("Stage 1/4: Slide processing - Preparing slides for analysis...", color="info")
                elif elapsed_time <= 30:
                    # Stage 2: 20% to 80%
                    progress_value = min(20 + ((elapsed_time - 5) / 25) * 60, 80)
                    status_text = dbc.Alert("Stage 2/4: Generating observations - Analyzing slide content...", color="info")
                elif elapsed_time <= 45:
                    # Stage 3: 80% to 95%
                    progress_value = min(80 + ((elapsed_time - 30) / 15) * 15, 95)
                    status_text = dbc.Alert("Stage 3/4: Generating headlines - Creating impactful headlines...", color="info")
                else:
                    # Stage 4: 95% to 99%
                    progress_value = min(95 + ((elapsed_time - 45) / 15) * 4, 99)
                    status_text = dbc.Alert("Stage 4/4: Updating presentation - Inserting headlines into slides...", color="info")

                return int(progress_value), status_text, False, {"display": "block"}, dash.no_update

        return dash.no_update, dash.no_update, False, dash.no_update, dash.no_update

    except Exception as e:
        print(f"Error polling job status: {str(e)}")
        return dash.no_update, dash.no_update, False, dash.no_update, dash.no_update

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
