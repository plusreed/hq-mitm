from mitmproxy import ctx, http
from typing import Union

json_dir = f"./json/"

map = {
    "/config": "app_config.json",
    "/config/admin": "app_config_admin.json",
    "/config/public": "app_config_public.json",
    "/shows/schedule": "schedule.json",
    "/store/products": "store.json",
}

"""
Addon for mitmproxy to mainly help with HQ reverse engineeringl
"""
class HQUtils:
    """ Checks if a local file exists in json_dir. """
    def get_local_file(self, file_path: str) -> Union[str, None]:
        try:
            file = open(f"{json_dir}{file_path}", "r")
        except OSError:
            ctx.log.info(f"get_local_file: error opening file {file_path}")
            return None

        with file:
            return file.read()


    """ Just checks if a path exists in the map dict. """
    def exists_in_map(self, key: str) -> bool:
        return key in map


    """ Super simple map_local. Less capable than mitmproxy's actual map_local stuff, but easier to work with (IMO.) """
    def map_local(self, path: str, flow: http.HTTPFlow) -> None:
        if self.exists_in_map(path):
            # get the file
            file = self.get_local_file(map[path])

            if type(file) == str:  # get_local_file returned some file
                # there is a file, send it
                ctx.log.debug(f"mapping local file {map[path]} to {path}")
                flow.response = http.Response.make(
                    200, file, {"Content-Type": "application/json"}
                )


    """ Intercept request if the host is HQ. """
    def request(self, flow: http.HTTPFlow) -> None:
        # check both prod and normal url. They're the same but w/e.
        if flow.request.host == "api-quiz.hype.space":
            # URL is from HQ
            
            # lol wtf
            url_path = f"/{'/'.join(flow.request.path_components)}"
            ctx.log.debug(f"request: path = {url_path}")

            self.map_local(url_path, flow)
        else:
            ctx.log.debug("not hq domain, passing")


addons = [HQUtils()]
