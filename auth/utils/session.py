
def clear_session(session):
    session["name"] = "auth"
    session["state"] = ""
    session["nonce"] = ""
    session["auth"] = False
    session["auth_errors"] = []
    session["auth_nameid"] = ""
    session["auth_sessionindex"] = ""
    session["auth_attributes"] = ""
