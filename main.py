import usb.core
import usb.util
import sys
from caracter_maps import Caracter

class ReadUsbQrcode():
    def __init__(self,VENDOR,PRODUCT,INTERFACE):
        dev = self.verify_dev(VENDOR,PRODUCT)       
        self.set_interface(INTERFACE)
        
        if dev.is_kernel_driver_active(INTERFACE):
            print("Desacoplando do kernel.")
            dev.detach_kernel_driver(INTERFACE)

        #Seta uma configuração padrão no dispositivo. É opcional passar parametros
        dev.set_configuration()
    
    def verify_dev(self,VENDOR,PRODUCT):
        dev = usb.core.find(idVendor = VENDOR, idProduct=PRODUCT)        
        try:
            if dev is None:
                raise ValueError('Device not found')                   
                
        except Exception as e:
            print("Houve um erro desconhecido.")

        self.set_dev(dev)
        return dev
    
    def set_interface(self,interface):
        self.interface = interface
    
    def get_interface(self):
        return self.interface

    def set_dev(self,dev):
        self.dev = dev

    def get_dev(self):
        return self.dev

    def get_config(self,dev):
        cfg = dev.get_active_configuration()
        return cfg

    def get_endpoint_in(self,cfg,ENDPOINT_IN):
        #Pega a primeira interface
        intf = cfg[(0,0)]
        # Get Endpoint de entrada de dados
        ep_in = intf[ENDPOINT_IN] 
        return ep_in

    def read_qrcode(self,ENDPOINT_IN):
        dev = self.get_dev()
        cfg = self.get_config(dev)
        ep_in = self.get_endpoint_in(cfg,ENDPOINT_IN)
        char = Caracter()
        qrcode = ""
        data = ""
        marc = -1
        i = 0
        while True:                        
            while marc != 1:                             
                try:        
                    data = dev.read(ep_in.bEndpointAddress,ep_in.wMaxPacketSize,10000)                    
                    #print("Valor do caractere",char.hid2ascii(data))
                    if data[2] == 40:
                        marc = 1
                    #    break 
                    #print("data", data)
                    qrcode = qrcode + char.hid2ascii(data)
                    
                except usb.core.USBError as e:
                    data = None
                    if e.args == ('Operation timed out',):
                        continue    
                except KeyboardInterrupt as k:    
                    self.attach_kernel(dev,self.get_interface())
                    print("Voce pressionou Ctrl+C para interromper este programa")
                    sys.exit()
            i += 1    
            print(f"{i} - Valor do qrcode: {qrcode}" )
            qrcode = ""
            marc = -1        
        
    
    def attach_kernel(self,dev,interface):
        #Release the device
        usb.util.release_interface(dev,interface)
        #Reattach the device to the OS kernel
        dev.attach_kernel_driver(interface)
    
    def reset_dev(self,dev):
        dev.reset()

if __name__ == '__main__':

    VENDOR = 0x0525  #Identificação do vendor
    PRODUCT = 0xa4ac #Idenficação do produto
    INTERFACE = 0  #Identificação de qual interface usar. Nesse caso tem apenas uma
    ENDPOINT_IN = 0  #Endpoint de entrada da Interface 0
    ENDPOINT_OUT = 1 #Endpoint de saida da Interface 0

    qrcode = ReadUsbQrcode(VENDOR,PRODUCT,INTERFACE)
    qrcode.read_qrcode(ENDPOINT_IN)