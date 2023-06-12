def check_prefix(content, prefix_list):
    for prefix in prefix_list:
        if content.startswith(prefix):
            return prefix
    return None


def is_wx_account(id):
    if id is None:
        return False
    return not id.lower().startswith("gh_")
