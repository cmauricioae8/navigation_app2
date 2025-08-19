
"""
Joystick component for controlling a robot's movement.
It uses a gesture detector to track the joystick's position and sends velocity commands
to a server via a socket client when the joystick is moved or released.
"""

import flet as ft
import asyncio

st_size = 200
gd_size = 50
neutral_p = (st_size-gd_size)/2

def on_pan_update(e, sio_client, V_max=0.4, W_max=1.0):
    if e.control.top + e.delta_y > neutral_p*2:
        e.control.top = neutral_p*2
    else:
        e.control.top = max(0, e.control.top + e.delta_y)

    if e.control.left + e.delta_x > neutral_p*2:
        e.control.left = neutral_p*2
    else:
        e.control.left = max(0, e.control.left + e.delta_x)

    #Compute velocities according to the maximum limits
    if neutral_p - e.control.top > 0.0:
        v = V_max
    else:
        v = -V_max
        if v < 0.0:
            v = -v
            # self.txtF_lin_min_vel.value = "-0.2" #Reset the incorrect value
    
    v = v*(neutral_p - e.control.top)/neutral_p
    w = W_max*(neutral_p - e.control.left)/neutral_p

    asyncio.run_coroutine_threadsafe(
        sio_client.send_velocity_command(v,w),
        sio_client._loop
    )
    e.control.update()


def on_pan_end(e, sio_client):
    e.control.left=neutral_p
    e.control.top=neutral_p
    asyncio.run_coroutine_threadsafe(
        sio_client.send_velocity_command(0.0, 0.0),
        sio_client._loop
    )
    e.control.update()


joystick_gd = ft.GestureDetector(
    mouse_cursor=ft.MouseCursor.MOVE, drag_interval=50,
    content=ft.Container(
        bgcolor=ft.Colors.BLUE,
        width=gd_size, height=gd_size,
        border_radius=25
    ),
    width=gd_size, height=gd_size,
    left=neutral_p, top=neutral_p, 
)

bg_img = ft.Image( width=st_size, height=st_size, fit=ft.ImageFit.CONTAIN,
    border_radius=ft.border_radius.all(st_size/2),
    src="/img/joystick_bg.png",
)

joystick = ft.Row(
    [
        ft.Stack([bg_img, joystick_gd], width=st_size, height=st_size)
    ],
    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
    visible=False,
)

