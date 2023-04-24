class PhantomListEntry:
    def __init__(self, socket_number, local_phantom, dx1_phantom, dx3_phantom, local_pad, dx1_pad, dx3_pad, slink_phantom, slink_pad):
        self.socket_number = socket_number
        self.local_phantom = local_phantom
        self.dx1_phantom = dx1_phantom
        self.dx3_phantom = dx3_phantom
        self.local_pad = local_pad
        self.dx1_pad = dx1_pad
        self.dx3_pad = dx3_pad
        self.slink_phantom = slink_phantom
        self.slink_pad = slink_pad

    def get_socket_number(self):
        return self.socket_number

    def get_socket_number_dlive(self):
        return self.get_socket_number()-1

    def get_local_phantom(self):
        return self.local_phantom

    def get_dx1_phantom(self):
        return self.dx1_phantom

    def get_dx3_phantom(self):
        return self.dx3_phantom

    def get_local_pad(self):
        return self.local_pad

    def get_dx1_pad(self):
        return self.dx1_pad

    def get_dx3_pad(self):
        return self.dx3_pad

    def get_slink_phantom(self):
        return self.slink_phantom

    def get_slink_pad(self):
        return self.slink_pad
