# from nicegui import ui
# from ns2.lib.logs import FetchLogs


# async def logs_page():
#     global log_panel
#     ui.label("System Logs").classes("text-h5")

#     with ui.card():
#         with ui.row():

#             def selects_change_cb():
#                 fetch_logs(daterange.value, level.value, identifier.value)

#             daterange = ui.select(
#                 options=[
#                     "Last 24 hours",
#                     "Last 7 days",
#                     "Current boot",
#                     "Previous boot",
#                 ],
#                 value="Last 24 hours",
#                 on_change=selects_change_cb,
#             )

#             level = ui.select(
#                 value="Error and above",
#                 options=[
#                     "Only emergency",  # 0
#                     "Alert and above",  # 1
#                     "Critical and above",  # 2
#                     "Error and above",  # 3
#                     "Warning and above",  # 4
#                     "Notice and above",  # 5
#                     "Info and above",  # 6
#                     "Debug and above",  # 7
#                 ],
#                 on_change=selects_change_cb,
#             )

#             identifier = ui.select(
#                 value="all",
#                 options=["all", "lots"],
#                 on_change=selects_change_cb,
#             )

#     log_panel = ui.log()

#     fetch_logs("Last 1 hour", "Info and above", "any")

#     return
