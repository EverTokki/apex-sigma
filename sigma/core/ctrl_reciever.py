import time
import msgpack
import zmq


class CtrlReciever():

    context = zmq.Context()

    def __init__(self, ev, ip, port, handler):
        self.handler = handler
        self.ev      = ev

        self.socket = CtrlReciever.context.socket(zmq.PULL)
        self.socket.connect('tcp://%s:%s' % (ip, port))


    async def read_data(self):
        try: await self.handler(self.ev, self.socket.recv_json(zmq.NOBLOCK))
        except zmq.error.Again: time.sleep(0.1)
