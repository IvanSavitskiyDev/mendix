from webapp.views.default import initiate, download, hello


def setup_routes(app):
    app.router.add_route("POST", "/initiate", initiate)
    app.router.add_route("GET", "/download/{download_id}", download)
    app.router.add_route("GET", "/hello", hello)
