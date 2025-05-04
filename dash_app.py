import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import requests
import os
import base64
from dotenv import load_dotenv

# Keep your existing imports for the Headlines AI page
# e.g., time, io, pathlib, etc., if you need them for the callbacks

from params import DEFAULT_FEW_SHOT_EXAMPLES

# Load environment variables
load_dotenv()

# Determine if we're in production
is_production = os.getenv("DEPLOYMENT_ENV") == "production"
API_URL = os.getenv("API_URL", "https://insightgen-api-xxxxxx.us-central1.run.app" if is_production else "http://localhost:8080")

print(f"Using API URL: {API_URL}")

# External stylesheets
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://use.fontawesome.com/releases/v5.15.4/css/all.css"
]

################################################################################
# PAGE 0: HOME PAGE
################################################################################

def home_layout():
    """
    Layout for the homepage with instructions on how to use the app.
    """
    return html.Div([
        html.H1("Welcome to InsightGen", className="mt-4 mb-3"),
        html.P(
            "InsightGen uses vision and language AI to analyze market research reports "
            "and generate insightful headlines and observations.",
            className="lead mb-4"
        ),

        dbc.Card([
            dbc.CardHeader(html.H4("How It Works", className="m-0")),
            dbc.CardBody([
                html.H5("The process works in two steps:"),
                html.Ol([
                    html.Li([
                        html.Strong("Observations Generation: "),
                        "Extracts relevant information from slides using vision models."
                    ]),
                    html.Li([
                        html.Strong("Headlines Generation: "),
                        "Provides a crisp summary from the generated observations."
                    ])
                ]),
                html.Hr(),
                html.H5("Instructions for Use:"),
                html.Ul([
                    html.Li("Currently only supports BGS studies"),
                    html.Li("Ensure PPTX has not hidden slides; PDF is identical to PPTX"),
                    html.Li("Ensure header slides layout starts with 'HEADER'"),
                    html.Li("Include client brands, competitors, market, etc. in the prompt"),
                    html.Li("You can add additional instructions as needed")
                ]),
                html.Hr(),
                html.H5("About Generators:"),
                html.P(
                    "Generators can be built to suit your specific task or study type. "
                    "They may need many trial and errors to perfect. "
                    "Each generator is designed to understand specific types of market research data."
                ),
                html.Div([
                    dbc.Button(
                        [html.I(className="fas fa-chart-line me-2"), "Get Started with Headlines AI"],
                        color="primary",
                        href="/headlines-ai",
                        className="mt-3"
                    )
                ], className="text-center")
            ])
        ], className="mb-4"),
    ])

################################################################################
# PAGE 1: HEADLINES AI (existing code from your main content)
################################################################################

def headlines_ai_layout():
    """
    Layout for the 'Headlines AI' page, which includes:
    - File upload
    - Inspection
    - Processing form
    - Progress bar and results
    """
    return html.Div([
        html.H2("Headlines AI", className="mb-3"),
        html.P(
            "Generate insightful headlines for your market research presentations.",
            className="text-muted mb-4"
        ),

        dbc.Row([
            # Left column: File upload and processing
            dbc.Col([
        # File upload section
        dbc.Card([
            dbc.CardHeader("Upload Files"),
            dbc.CardBody([
                        # PPTX upload
                        html.P("Upload PPTX file", className="mb-1 small"),
                        dcc.Upload(
                            id='upload-pptx',
                            children=html.Div([
                                html.I(className="fas fa-file-powerpoint me-2"),
                                'Drag and Drop or ',
                                html.A('Select PPTX File')
                            ], className="small"),
                            style={
                                'width': '100%',
                                'height': '45px',
                                'lineHeight': '45px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin-bottom': '15px'
                            },
                            multiple=False
                        ),
                        html.Div(id='pptx-upload-output', className="small"),

                        # PDF upload
                        html.P("Upload PDF file", className="mb-1 mt-3 small"),
                        dcc.Upload(
                            id='upload-pdf',
                            children=html.Div([
                                html.I(className="fas fa-file-pdf me-2"),
                                'Drag and Drop or ',
                                html.A('Select PDF File')
                            ], className="small"),
                            style={
                                'width': '100%',
                                'height': '45px',
                                'lineHeight': '45px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin-bottom': '15px'
                            },
                            multiple=False
                        ),
                        html.Div(id='pdf-upload-output', className="small"),

                        # Submit button with loading indicator
                        html.Div([
                            dbc.Button(
                                [
                                    html.Span(id="inspect-button-text", children="Inspect Files"),
                                    html.Div(id="inspect-spinner", className="ms-2 d-none")
                                ],
                                id="inspect-button",
                                color="primary",
                                className="mt-3 w-100",
                                n_clicks=0
                            )
                        ], className="text-center")
            ])
        ], className="mb-4"),

                # Processing form section
                html.Div(id="processing-form-container", style={"display": "none"}),

                # Keep an empty processing status container for callback references
                html.Div(id="processing-status-container", style={"display": "none"}),
            ], width=7),

            # Right column: Inspection results and final results
            dbc.Col([
        # Inspection results section
        html.Div(id="inspection-results-container", style={"display": "none"}),

        # Results section
        html.Div(id="results-container"),
            ], width=5),
        ]),
    ])

################################################################################
# PAGE 2: GENERATORS (dummy boxes)
################################################################################

def generators_layout():
    """
    Layout for the 'Generators' page, showing placeholder inputs for future development.
    """
    return html.Div([
        html.H1("Generators", className="mt-4 mb-3"),
        html.P(
            "Create or modify your AI prompts here. (Placeholder UI for future development.)",
            className="lead mb-4"
        ),

        dbc.Card([
            dbc.CardHeader("Observation Prompt"),
            dbc.CardBody([
                dbc.Textarea(
                    id="observation-prompt",
                    placeholder="Enter your observation prompt here...",
                    style={"height": "100px"}
                ),
            ])
        ], className="mb-4"),

        dbc.Card([
            dbc.CardHeader("Headline Instructions"),
            dbc.CardBody([
                dbc.Textarea(
                    id="headline-instructions",
                    placeholder="Enter your headline generation instructions here...",
                    style={"height": "100px"}
                ),
            ])
        ], className="mb-4"),

        dbc.Card([
            dbc.CardHeader("Knowledge Base (Future Feature)"),
            dbc.CardBody([
                dbc.Textarea(
                    id="knowledge-base",
                    placeholder="Attach relevant knowledge or references here...",
                    style={"height": "100px"}
                ),
            ])
        ], className="mb-4"),

        dbc.Alert("Note: These fields are placeholders for a future feature.", color="info")
    ])

################################################################################
# PAGE 3: LOGS (empty page)
################################################################################

def logs_layout():
    """
    Layout for the 'Logs' page (currently empty).
    """
    return html.Div([
        html.H1("Logs", className="mt-4 mb-3"),
        html.P("This page will show logs and history of processed presentations in the future.")
    ])

################################################################################
# PAGE 4: ABOUT INSIGHTGEN
################################################################################

def about_layout():
    """
    Layout for the 'About InsightGen' page, which includes instructions, app info, etc.
    """
    return html.Div([
        html.H1("About InsightGen", className="mt-4 mb-3"),
        html.Hr(),
        html.P(
            "InsightGen uses vision and language AI to analyze market research reports "
            "and generate insightful headlines and observations.",
            className="lead"
        ),
        html.P("Version: 0.1.0"),
        html.P("Developed by: Sumit Kamra"),

        html.H5("Instructions", className="mt-4"),
        html.Ul([
            html.Li("Currently only supports BGS studies"),
            html.Li("Ensure PPTX has not hidden slides; PDF is identical to PPTX"),
            html.Li("Ensure header slides layout starts with 'HEADER'"),
            html.Li("Include client brands, competitors, market, etc. in the prompt"),
            html.Li("You can add additional instructions as needed")
        ]),
        html.H5("API Status", className="mt-4"),
        # We'll reuse the same approach to show the API status if needed
        html.Div(id="api-status-about")
    ])

################################################################################
# DASH APP SETUP
################################################################################

app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True)
server = app.server
app.title = "InsightGen: AI-Powered Insights"

# We'll store your existing callbacks in this file
# or define them below. For a multi-page app, we can keep
# them here, referencing the IDs from the Headlines AI layout.

# Create a simple sidebar with nav links
sidebar = html.Div([
    # Logo and title at the top
    html.A([
        html.Div([
            html.Img(src="/assets/insightgen_logo.svg", className="sidebar-logo"),
            html.H4("InsightGen", className="app-title")
        ], className="sidebar-header d-flex align-items-center")
    ], href="/", id="logo-home-link", style={"text-decoration": "none"}),

    # Navigation links
    dbc.Nav(
        [
            dbc.NavLink([
                html.I(className="fas fa-chart-line"),
                "Headlines AI"
            ], href="/headlines-ai", active="exact", className="py-2"),

            dbc.NavLink([
                html.I(className="fas fa-cogs"),
                "Generators"
            ], href="/generators", active="exact", className="py-2"),

            dbc.NavLink([
                html.I(className="fas fa-history"),
                "Logs"
            ], href="/logs", active="exact", className="py-2"),

            dbc.NavLink([
                html.I(className="fas fa-info-circle"),
                "About InsightGen"
            ], href="/about", active="exact", className="py-2"),
    ],
    vertical=True,
    pills=True,
        className="flex-column p-3 flex-grow-1",
    ),

    # Version at the bottom
    html.Div([
        html.P("Version: 0.1.0", className="text-muted small mb-0 text-center")
    ], className="mt-auto p-3 border-top")
], className="h-100 d-flex flex-column")

# Define a container that shows the selected page's layout
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    dbc.Row([
        dbc.Col(sidebar, width=2, className="sidebar p-0"),
        dbc.Col(html.Div(id='page-content', className="content-area"), width=10),
    ], className="g-0", style={"height": "100vh"}),

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

    # JavaScript for button loading indicators
    html.Div([
        html.Script('''
            document.addEventListener('DOMContentLoaded', function() {
                // Function to show spinner when button is clicked
                function setupButtonSpinner(buttonId, spinnerId) {
                    const button = document.getElementById(buttonId);
                    const spinner = document.getElementById(spinnerId);

                    if (button && spinner) {
                        button.addEventListener('click', function() {
                            spinner.classList.remove('d-none');
                            spinner.classList.add('d-inline-block');
                        });
                    }
                }

                // Setup for inspect button
                setupButtonSpinner('inspect-button', 'inspect-spinner');

                // Setup for process button
                setupButtonSpinner('process-button', 'process-spinner');
            });
        ''')
    ]),
], fluid=True)

################################################################################
# NAVIGATION CALLBACK
################################################################################

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    """
    A simple router callback that returns the appropriate layout
    depending on the URL path.
    """
    if pathname == "/headlines-ai":
        return headlines_ai_layout()
    elif pathname == "/generators":
        return generators_layout()
    elif pathname == "/logs":
        return logs_layout()
    elif pathname == "/about":
        return about_layout()
    else:
        # Default to Home page if path is unknown or root
        return home_layout()

################################################################################
# HEADLINES AI CALLBACKS (same as your existing code)
################################################################################

# For brevity, we'll show only a couple of them.
# Copy your existing callback definitions here, referencing the same IDs:
# - upload-pptx, upload-pdf, inspection-results-container, etc.

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

# Callback to inspect files
@callback(
    Output('inspection-results-store', 'data'),
    Output('inspection-results-container', 'children'),
    Output('inspection-results-container', 'style'),
    Output('inspect-button-text', 'children'),
    Output('inspect-spinner', 'className'),
    Input('inspect-button', 'n_clicks'),
    State('pptx-store', 'data'),
    State('pdf-store', 'data'),
    prevent_initial_call=True
)
def inspect_files(n_clicks, pptx_data, pdf_data):
    if n_clicks == 0 or pptx_data is None or pdf_data is None:
        raise PreventUpdate

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
            return None, dbc.Alert(f"Error during inspection: {error_detail}", color="danger"), {"display": "block"}, "Inspect Files", "ms-2 d-none"

        # Process successful response
        inspection_results = response.json()

        # Create a simplified results display
        stats = inspection_results.get("slide_stats", {})
        total_slides = stats.get("total_slides", 0)
        header_count = stats.get("header_slides", {}).get("count", 0)
        content_count = stats.get("content_slides", {}).get("count", 0)
        missing_count = stats.get("missing_placeholders", {}).get("count", 0)

        # Create a simplified card with key stats
        results_display = dbc.Card([
            dbc.CardHeader("Inspection Results"),
            dbc.CardBody([
                html.H5("File Analysis Complete", className="text-success mb-3"),

                # Stats in a table format
                html.Table([
                    html.Tr([
                        html.Td("Total Slides:", className="pe-3"),
                        html.Td(html.Strong(total_slides))
                    ]),
                    html.Tr([
                        html.Td("Header Slides:", className="pe-3"),
                        html.Td(html.Strong(header_count))
                    ]),
                    html.Tr([
                        html.Td("Content Slides:", className="pe-3"),
                        html.Td(html.Strong(content_count))
                    ]),
                    html.Tr([
                        html.Td("Missing Placeholders:", className="pe-3"),
                        html.Td(html.Strong(missing_count, className="text-danger" if missing_count > 0 else ""))
                    ])
                ], className="mb-3"),

                # Warnings if any
                html.Div([
                    dbc.Alert(
                        "Some slides are missing title placeholders. Headlines cannot be inserted into these slides.",
                        color="warning",
                        className="small p-2 mb-0"
                    ) if missing_count > 0 else None
                ])
            ])
        ])

        return inspection_results, results_display, {"display": "block"}, "Inspect Files", "ms-2 d-none"

    except requests.RequestException as e:
        return None, dbc.Alert(f"Error connecting to API: {str(e)}", color="danger"), {"display": "block"}, "Inspect Files", "ms-2 d-none"
    except Exception as e:
        return None, dbc.Alert(f"Error: {str(e)}", color="danger"), {"display": "block"}, "Inspect Files", "ms-2 d-none"

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
                    html.Label("Select Generator", className="small"),
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
                    html.Label("Prompt: Market, Brand Context and Additional Instructions", className="small"),
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
                    html.Label("Slide Memory", className="small"),
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
                    dbc.Button(
                        [
                            html.Span(id="process-button-text", children="Generate Headlines"),
                            html.Div(id="process-spinner", className="ms-2 d-none")
                        ],
                        id="process-button",
                        color="primary",
                        className="w-100"
                    )
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
    Output('results-container', 'children'),
    Output('process-button-text', 'children'),
    Output('process-spinner', 'className'),
    Input('process-button', 'n_clicks'),
    State('pptx-store', 'data'),
    State('pdf-store', 'data'),
    State('generator-dropdown', 'value'),
    State('user-prompt', 'value'),
    State('context-window-size', 'value'),
    prevent_initial_call=True
)
def process_files(n_clicks, pptx_data, pdf_data, generator_id, user_prompt, context_window_size):
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

        # Submit job
        response = requests.post(f"{API_URL}/upload-and-process/", files=files, data=data)

        # Check for HTTP errors
        if response.status_code >= 400:
            error_detail = response.json().get("detail", "Unknown error")

            # Handle specific validation errors
            if "Slide count mismatch" in error_detail:
                return None, True, {"display": "none"}, dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    f"{error_detail}",
                    html.P("Please ensure both files have the same number of slides before proceeding.", className="mt-2")
                ], color="danger"), "Generate Headlines", "ms-2 d-none"
            elif "Unsupported or corrupt" in error_detail or "Invalid or corrupt" in error_detail:
                return None, True, {"display": "none"}, dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    f"{error_detail}",
                    html.P("Please check your files and try again with valid formats.", className="mt-2")
                ], color="danger"), "Generate Headlines", "ms-2 d-none"
            else:
                return None, True, {"display": "none"}, dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    f"Error: {error_detail}"
                ], color="danger"), "Generate Headlines", "ms-2 d-none"

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

        # Initial button text with status
        process_button_text = "Processing (5%) - Slide processing..."

        return job_id, False, {"display": "none"}, html.Div(warnings_display), process_button_text, "ms-2 d-inline-block"

    except requests.RequestException as e:
        return None, True, {"display": "none"}, dbc.Alert(f"Error connecting to API: {str(e)}", color="danger"), "Generate Headlines", "ms-2 d-none"
    except Exception as e:
        return None, True, {"display": "none"}, dbc.Alert(f"Error: {str(e)}", color="danger"), "Generate Headlines", "ms-2 d-none"

# Callback to update job status
@callback(
    Output('processing-completed', 'data'),
    Output('processing-status-container', 'style', allow_duplicate=True),
    Output('results-container', 'children', allow_duplicate=True),
    Output('process-button-text', 'children', allow_duplicate=True),
    Output('process-spinner', 'className', allow_duplicate=True),
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
                        html.H5("Performance Metrics", className="mt-4 mb-3"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("Total Slides", className="small text-muted mb-1"),
                                        html.H4(metrics.get("total_slides", 0))
                                    ], className="p-2")
                                ], className="text-center mb-3")
                            ], width=6),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("Content Slides", className="small text-muted mb-1"),
                                        html.H4(metrics.get("content_slides_processed", 0))
                                    ], className="p-2")
                                ], className="text-center mb-3")
                            ], width=6),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("Observations", className="small text-muted mb-1"),
                                        html.H4(metrics.get("observations_generated", 0))
                                    ], className="p-2")
                                ], className="text-center mb-3")
                            ], width=6),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("Headlines", className="small text-muted mb-1"),
                                        html.H4(metrics.get("headlines_generated", 0))
                                    ], className="p-2")
                                ], className="text-center mb-3")
                            ], width=6)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("Processing Time", className="small text-muted mb-1"),
                                        html.H4(f"{round(metrics.get('total_time_seconds', 0), 1)}s")
                                    ], className="p-2")
                                ], className="text-center mb-3")
                            ], width=12)
                        ])
                    ]

                # Create download button
                download_url = f"{API_URL}/download/{job_id}"
                download_filename = job_status.get("output_filename", f"processed_presentation.pptx")

                download_section = [
                    html.H5("Download Results", className="mt-4 mb-3"),
                    html.Div([
                        html.A([
                            html.I(className="fas fa-file-powerpoint fa-2x me-2 text-primary"),
                            html.Span(download_filename, className="text-primary")
                        ], href=download_url, download=download_filename, target="_blank", className="text-decoration-none")
                    ], className="text-center")
                ]

                # Combine all results
                new_results = dbc.Card([
                    dbc.CardHeader("Processing Results"),
                    dbc.CardBody([
                        dbc.Alert("Processing completed successfully!", color="success", className="mb-4"),
                        *metrics_display,
                        *download_section
                    ])
                ])

                # Reset the process button
                process_button_text = "Generate Headlines"
                process_spinner_class = "ms-2 d-none"

                # Hide the progress container when completed
                return True, {"display": "none"}, new_results, process_button_text, process_spinner_class

            elif status == "failed":
                # Reset the process button
                process_button_text = "Generate Headlines"
                process_spinner_class = "ms-2 d-none"

                return True, {"display": "none"}, dbc.Alert(f"Processing failed: {job_status.get('message', 'Unknown error')}", color="danger"), process_button_text, process_spinner_class

            else:  # processing
                # Calculate progress based on elapsed time
                elapsed_time = n_intervals  # Each interval is 1 second

                # Update progress based on elapsed time
                if elapsed_time <= 5:
                    # Stage 1: 5% to 20%
                    progress_value = min(5 + (elapsed_time / 5) * 15, 20)
                    detail_text = "Slide processing..."
                elif elapsed_time <= 30:
                    # Stage 2: 20% to 80%
                    progress_value = min(20 + ((elapsed_time - 5) / 25) * 60, 80)
                    detail_text = "Generating observations..."
                elif elapsed_time <= 45:
                    # Stage 3: 80% to 95%
                    progress_value = min(80 + ((elapsed_time - 30) / 15) * 15, 95)
                    detail_text = "Generating headlines..."
                else:
                    # Stage 4: 95% to 99%
                    progress_value = min(95 + ((elapsed_time - 45) / 15) * 4, 99)
                    detail_text = "Updating presentation..."

                # Update button text with progress and status
                process_button_text = f"Processing ({int(progress_value)}%) - {detail_text}"

                return False, {"display": "none"}, dash.no_update, process_button_text, "ms-2 d-inline-block"

        return False, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    except Exception as e:
        print(f"Error polling job status: {str(e)}")
        return False, dash.no_update, dash.no_update, dash.no_update, dash.no_update

################################################################################
# OPTIONAL: ABOUT PAGE CALLBACKS
################################################################################
# If you want to check API status in the About page, define a callback referencing "api-status-about".


################################################################################
# MAIN
################################################################################

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
