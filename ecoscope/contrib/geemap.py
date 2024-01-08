"""
MIT License

Copyright (c) 2020-2021, Qiusheng Wu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import ee
import os
import json

__version__ = "0.30.0"


def in_colab_shell():
    """Tests if the code is being executed within Google Colab."""
    import sys

    if "google.colab" in sys.modules:
        return True
    else:
        return False


def ee_initialize(
    token_name="EARTHENGINE_TOKEN",
    auth_mode="notebook",
    service_account=False,
    auth_args={},
    user_agent_prefix="geemap",
    **kwargs,
):
    """Authenticates Earth Engine and initialize an Earth Engine session

    Args:
        token_name (str, optional): The name of the Earth Engine token. Defaults to "EARTHENGINE_TOKEN".
        auth_mode (str, optional): The authentication mode, can be one of paste,notebook,gcloud,appdefault. Defaults to "notebook".
        service_account (bool, optional): If True, use a service account. Defaults to False.
        auth_args (dict, optional): Additional authentication parameters for aa.Authenticate(). Defaults to {}.
        user_agent_prefix (str, optional): If set, the prefix (version-less) value used for setting the user-agent string. Defaults to "geemap".
        kwargs (dict, optional): Additional parameters for ee.Initialize(). For example,
            opt_url='https://earthengine-highvolume.googleapis.com' to use the Earth Engine High-Volume platform. Defaults to {}.
    """
    import httplib2

    user_agent = f"{user_agent_prefix}/{__version__}"
    if "http_transport" not in kwargs:
        kwargs["http_transport"] = httplib2.Http()

    auth_args["auth_mode"] = auth_mode

    if ee.data._credentials is None:
        ee_token = os.environ.get(token_name)
        if in_colab_shell():
            from google.colab import userdata

            try:
                ee_token = userdata.get(token_name)
            except Exception:
                pass
        if service_account:
            try:
                credential_file_path = os.path.expanduser(
                    "~/.config/earthengine/private-key.json"
                )

                if os.path.exists(credential_file_path):
                    with open(credential_file_path) as f:
                        token_dict = json.load(f)
                else:
                    token_name = "EARTHENGINE_TOKEN"
                    ee_token = os.environ.get(token_name)
                    token_dict = json.loads(ee_token, strict=False)
                service_account = token_dict["client_email"]
                private_key = token_dict["private_key"]

                credentials = ee.ServiceAccountCredentials(
                    service_account, key_data=private_key
                )
                ee.Initialize(credentials, **kwargs)

            except Exception as e:
                raise Exception(e)

        else:
            try:
                if ee_token is not None:
                    credential_file_path = os.path.expanduser(
                        "~/.config/earthengine/credentials"
                    )
                    if not os.path.exists(credential_file_path):
                        os.makedirs(
                            os.path.dirname(credential_file_path), exist_ok=True
                        )
                        if ee_token.startswith("{") and ee_token.endswith(
                            "}"
                        ):  # deals with token generated by new auth method (earthengine-api>=0.1.304).
                            token_dict = json.loads(ee_token)
                            with open(credential_file_path, "w") as f:
                                f.write(json.dumps(token_dict))
                        else:
                            credential = (
                                '{"refresh_token":"%s"}' % ee_token
                            )  # deals with token generated by old auth method.
                            with open(credential_file_path, "w") as f:
                                f.write(credential)

                ee.Initialize(**kwargs)

            except Exception:
                ee.Authenticate(**auth_args)
                ee.Initialize(**kwargs)

    ee.data.setUserAgent(user_agent)
