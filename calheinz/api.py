import json

import requests as req
from fastapi import APIRouter, FastAPI

from ical import Event, EventDiff, get_events

app = FastAPI(title="calheinz API", openapi_url="/openapi.json")

api_router = APIRouter()


@api_router.get("/", status_code=200)
async def root() -> dict:
    return {"message": "Hello World"}


@api_router.get("/readurl", status_code=200)
async def readurl(url: str) -> str:
    if not url:
        return
    try:
        res = req.get(url)
    except req.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    else:
        pass

    return json.dumps([e.formatted() for e in get_events(res.content)])


# @api_router.get("/readurl", status_code=200)
# async def diff
#     lhs_events = from_url(lhs) if is_url(lhs) else from_file(lhs)
#     rhs_events = from_url(rhs) if is_url(rhs) else from_file(rhs)

#     # see https://stackoverflow.com/a/38240169
#     diffs = set(lhs_events) ^ set(rhs_events)
#     if len(diffs) < 1:
#         # no changes
#         return 0
#     diff_uids = {e.uid for e in diffs}

#     # identify added and removed events by uid set difference
#     lhs_uids = {e.uid for e in lhs_events}
#     rhs_uids = {e.uid for e in rhs_events}
#     added_uids = rhs_uids - lhs_uids
#     removed_uids = lhs_uids - rhs_uids

#     # if an event is different, but has neither
#     # been added or removed, it must have changed
#     changed_uids = diff_uids - (added_uids | removed_uids)

#     # lookup tables to build (old, new) tuples
#     lhs_dict = {e.uid: e for e in lhs_events}
#     rhs_dict = {e.uid: e for e in rhs_events}
#     added_events = [EventDiff(None, rhs_dict[u]) for u in added_uids]
#     removed_events = [EventDiff(lhs_dict[u], None) for u in removed_uids]
#     changed_events = [EventDiff(lhs_dict[u], rhs_dict[u]) for u in changed_uids]

#     # roll them into one list
#     diff_events = [*added_events, *removed_events, *changed_events]
#     print(format_difflist(diff_events))
#     return diff_events


app.include_router(api_router)

if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
