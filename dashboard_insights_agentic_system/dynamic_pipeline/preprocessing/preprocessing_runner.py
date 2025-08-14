# preprocessing.py
def preprocess_dashboard_data(connection_obj):
    if connection_obj["source"] == "powerbi":
        session = connection_obj["session"]
        # Example: list reports in workspace
        workspace_id = "YOUR_WORKSPACE_ID"
        reports = session.get(
            f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports"
        ).json()
        return reports

    elif connection_obj["source"] == "tableau":
        server = connection_obj["server"]
        # Example: list all views
        all_views, _ = server.views.get()
        return [{"name": v.name, "id": v.id} for v in all_views]