from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings


class Page(QWebEnginePage):
    def __init__(self, profile, window):
        super().__init__(profile, window)
        self.window_ref = window

        s = self.settings()
        s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanPaste, True)

        if hasattr(self, "permissionRequested"):          # newer PyQt6 (6.8+)
            self.permissionRequested.connect(lambda p: p.grant())
        else:                                              # older PyQt6
            self.featurePermissionRequested.connect(self.grant_feature)

    def grant_feature(self, origin, feature):
        self.setFeaturePermission(
            origin, feature, QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
        )

    def createWindow(self, _type):
        return self.window_ref.new_tab().page()

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        if url.scheme() in ("http", "https") and url.host() not in ("localhost", "127.0.0.1"):
            return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)