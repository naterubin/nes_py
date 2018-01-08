class CPU():
    def __init__(self, rom, ppu):
        self.rom = rom
        self.ppu = ppu
        self.ram = bytearray([0] * 0x800)

        self.a = 0
        self.x = 0
        self.y = 0
        self.pc = 0x4020
        self.sp = 0x1FF
        self.flags = {
            'negative': False,
            'overflow': False,
            'break': False,
            'decimal': False,
            'interrupt': True,
            'zero': False,
            'carry': False,
        }

    def byte_at_location(self, address):
        # Map memory to location
        if address <= 0x1FFF:
            idx = address % 0x800
            return self.ram[idx]
        elif address <= 0x3FFF:
            # ppu register
            pass
        elif address <= 0x4017:
            # apu/io registers
            pass
        elif address <= 0x401f:
            # cpu in test mode, error
            raise Exception("address not addressable when not in test mode")
        elif address <= 0xFFFF:
            idx = address - 0x4020
            return self.rom[idx]
        else:
            raise Exception("cannot address higher than $FFFF")

    def absolute_address(self):
        lb = self.byte_at_location(self.pc)
        self.pc += 1
        hb = self.byte_at_location(self.pc)
        self.pc += 1
        return int.from_bytes(bytearray([lb, hb]), byteorder='little')

    def stack_push(self, value):
        self.ram[self.sp] = value
        self.sp -= 1

    def stack_pop(self):
        val = self.ram[self.sp]
        self.sp += 1
        return val

    def adc(self, value):
        new_val = self.a + value
        if new_val > 0xFF:
            self.a = new_val % 0xFF
            self.flags['carry'] = True
        else:
            self.a = new_val
            self.flags['carry'] = False

    def process_opcode(self):
        opcode = self.byte_at_location(self.pc)
        self.pc += 1

        if opcode == 0x00:  # BRK
            break
        elif opcode == 0x18:  # CLC
            self.flags['carry'] = False
        elif opcode == 0x20:  # JSR oper
            lb = self.byte_at_location(self.pc)
            self.pc += 1
            hb = self.byte_at_location(self.pc)
            self.pc += 1
            address = int.from_bytes(bytearray([hb, lb]), byteorder='big')

            curr_lb, curr_hb = (self.pc - 1).to_bytes(2, byteorder='little')
            self.push_stack(curr_hb)
            self.push_stack(curr_lb)

            self.pc = address
        elif opcode == 0x38:  # SEC
            self.flags['carry'] = True
        elif opcode == 0x65:  # ADC oper
            self.adc(self.ram[self.byte_at_location(self.pc)])
            self.pc += 1
        elif opcode == 0x58:  # CLI
            self.flags['interrupt'] = False
        elif opcode == 0x60:  # RTS
            hb = self.pop_stack()
            lb = self.pop_stack()
            address = int.from_bytes(bytearray([hb, lb]), byteorder='big')
            self.pc = address + 1
        elif opcode == 0x69:  # ADC #oper
            self.adc(self.byte_at_location(self.pc))
            self.pc += 1
        elif opcode == 0x6D:  # ADC oper
            address = self.absolute_address()
            self.adc(self.byte_at_location(address))
        elif opcode == 0x75:  # ADC oper,X
            operator = self.byte_at_location(self.pc)
            self.pc += 1
            zp_addr = (operator + self.x) % 0xFF
            self.adc(self.byte_at_location(zp_addr))
        elif opcode == 0x78:  # SEI
            self.flags['interrupt'] = True
        elif opcode == 0x79:  # ADC oper,Y
            address = self.absolute_address() + self.y
            self.adc(self.byte_at_location(address))
        elif opcode == 0x7D:  # ADC oper,X
            address = self.absolute_address() + self.x
            self.adc(self.byte_at_location(address))
        elif opcode == 0xB8:  # CLV
            self.flags['overflow'] = False
        elif opcode == 0xD8:  # CLD
            self.flags['decimal'] = False
        elif opcode == 0xF8:  # SED
            self.flags['decimal'] = True


class PPU():
    def __init__(self):
        self.ctrl = 0
        self.mask = 0
        self.status = 0
        self.oam_addr = 0
        self.oam_data = 0
        self.scroll = 0
        self.addr = 0
        self.data = 0
        self.oam_dma = 0

    def get_register_value(self, address):
        if address == 0x2000:
            return self.ctrl
        elif address == 0x2001:
            return self.mask
        elif address == 0x2002:
            return self.status
        elif address == 0x2003:
            return self.oam_addr
        elif address == 0x2004:
            return self.oam_data
        elif address == 0x2005:
            return self.scroll
        elif address == 0x2006:
            return self.addr
        elif address == 0x2007:
            return self.data
        elif address == 0x4014:
            return self.oam_dma
        else:
            raise Exception("Not a PPU address")

    def set_register_value(self, address, value):
        if address == 0x2000:
            self.ctrl = value
        elif address == 0x2001:
            self.mask = value
        elif address == 0x2002:
            self.status = value
        elif address == 0x2003:
            self.oam_addr = value
        elif address == 0x2004:
            self.oam_data = value
        elif address == 0x2005:
            self.scroll = value
        elif address == 0x2006:
            self.addr = value
        elif address == 0x2007:
            self.data = value
        elif address == 0x4014:
            self.oam_dma = value
        else:
            raise Exception("Not a PPU address")
