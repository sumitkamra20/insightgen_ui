from dash_app import server

# This file is required by App Engine to serve the app
# The server variable is imported from dash_app.py

if __name__ == "__main__":
    # This block is not used by App Engine but can be used for local testing
    from dash_app import app
    app.run_server(debug=False, host='0.0.0.0', port=8080)
