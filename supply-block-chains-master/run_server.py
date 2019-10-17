from .blockchain import bc_app
# from waitress import serve

if __name__ == "__main__":
    # serve(bc_app, host='127.0.0.1', port=8000)
    bc_app.run('127.0.0.1', port=8081)
