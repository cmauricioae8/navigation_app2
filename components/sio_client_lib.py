import socketio
import asyncio
import threading

class SocketIOClient:
    def __init__(self, server_url):
        self.server_url = server_url
        self.sio = socketio.AsyncClient()
        self._thread = None
        self._loop = None
        self.connected = False
        self.function_mode = "static"
        self.in_waiting = False

        # Register event handlers
        @self.sio.event
        async def connect():
            print('Connected to server.')

        @self.sio.event
        async def disconnect():
            print('Disconnected from server.')
        
        @self.sio.on('*')
        def catch_all(event, data):
            print(f'Received event "{event}" with data {data}')
        
        ## Callback function for the 'on_status_change' event, the change mode event
        @self.sio.on('on_status_change')
        def handle_status_change(msg):
            # To correctly obtain message information, please refer to SocketIO server documentation
            try:
                data_val = msg['data']
                # print(f"{data_val=}")
                
                operation_mode_val = data_val['operation_mode']
                mode_val = operation_mode_val['mode']
                ready_val = operation_mode_val['ready']

                if mode_val is not None and ready_val is not None:
                    # print(f"Received on_status_change complete")
                    self.function_mode = mode_val
                else:
                    print("Received 'on_status_change' event, but data is incomplete.")

            except Exception as e:
                print(f"Error processing 'on_status_change' data: {e}")

        

    async def _run_sio_client(self):
        """Internal method to run the Socket.IO client in the event loop."""
        try:
            await self.sio.connect(self.server_url)
            await self.sio.wait()
        except Exception as e:
            print(f"Connection failed: {e}")

    def start(self):
        """Starts the Socket.IO client in a new thread."""
        if self._thread is None or not self._thread.is_alive():
            def run_loop():
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
                self._loop.run_until_complete(self._run_sio_client())

            self._thread = threading.Thread(target=run_loop, daemon=True)
            self._thread.start()
            print("Socket.IO client thread started.")
            self.connected = True

    async def send_velocity_command(self, linear_x, angular_z):
        """Sends the 'cmd_vel' event to the server."""
        # To correctly emit event, please refer to SocketIO server documentation
        if not self.sio.connected:
            print("Client not connected.")
            return

        data = {
            'linear_x': linear_x,
            'angular_z': angular_z
        }
        await self.sio.emit('cmd_vel', data)
        # print(f"Sent 'cmd_vel': linear_x={linear_x}, angular_z={angular_z}")        

    def disconnect(self):
        """Disconnects the client."""
        if self.sio.connected:
            asyncio.run_coroutine_threadsafe(self.sio.disconnect(), self._loop)
            print("Disconnect command sent.")