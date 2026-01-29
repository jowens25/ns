from nicegui import ui, app


def init_colors():
    ui.colors(
        primary="#ffffff",
        secondary="#191a1a",
        accent="#ff0000",
        dark="#1f2121",
        dark_page="#121212",
        positive="#21ba45",
        negative="#c10015",
        info="#31ccec",
        warning="#f2c037",
        firewallcard="#3A3D3D")

    dark = ui.dark_mode()
    dark.enable()
    ui.query("body").classes("bg-secondary")



# background #191a1a

# menu color #1f2121
