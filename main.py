from app import create_app

app = create_app()

if __name__ == "__main__":
    # Use threaded=True and disable reloader for better stability in containerized environments
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True, use_reloader=False)