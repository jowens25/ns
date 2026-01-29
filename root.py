from nicegui import ui, app
from theme import init_colors
from rest_api import get_pps_ave_diff
#from  snmp.snmp import GetUsers

def clear_user():
    print("hello")
    app.storage.user.clear()




async def root_page():
    
    ui.label("Overview - root page").classes("text-h5")
    
    

    #v2s, v3s = GetUsers()
    #print(v2s, v3s)
    #ui.button("clear",  on_click= clear_user)

    #values = []
    #async def update_value():
    #    print("test")
    #    values.append(await get_pps_ave_diff())
#
    #ui.timer(1, update_value)
#
    #ui.echart({
    #'xAxis': {'type': 'category'},
    #'yAxis': {'axisLabel': {':formatter': 'value => "$" + value'}},
    #'series': [{'type': 'line', 'data': values}],
#})