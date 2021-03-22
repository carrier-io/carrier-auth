#   Copyright 2020 getcarrier.io
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


def clear_session(session):
    session["name"] = "auth"
    session["state"] = ""
    session["nonce"] = ""
    session["auth"] = False
    session["auth_errors"] = []
    session["auth_nameid"] = ""
    session["auth_sessionindex"] = ""
    session["auth_attributes"] = ""