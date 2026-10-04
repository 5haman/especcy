"""Electrical design inputs. Coordinates are the existing CAD's millimetres.

Schematic labels define connections; placement does not imply routing.
Dimensions are conservative package envelopes, not fabrication tolerances.
"""

DATE = '2026-10-04'
REVISION = 'A - unrouted study'

SYMBOLS = {
    'ESP32': 'RF_Module:ESP32-WROOM-32E',
    'LDO': 'Regulator_Linear:TLV75733PDBV',
    'USB': 'Connector:USB_B_Micro',
    'R': 'Device:R', 'C': 'Device:C', 'Fuse': 'Device:Polyfuse',
    'TVS': 'Device:D_TVS', 'Switch': 'Switch:SW_Push',
    'LCD': 'Connector_Generic:Conn_01x08',
    'Pogo': 'Connector_Generic:Conn_01x06',
    'Adapter': 'Connector_Generic:Conn_01x04',
    'PowerPort': 'Connector_Generic:Conn_01x02',
    'Comparator': 'Comparator:TLV7041DBV',
    'Reference': 'Reference_Voltage:LM4040DBZ-2.0',
    'Buffer': '74xGxx:74LVC2G125', 'Flag': 'power:PWR_FLAG',
}

FOOTPRINTS = {
    'ESP32': 'RF_Module:ESP32-WROOM-32E',
    'SOT23_5': 'Package_TO_SOT_SMD:SOT-23-5',
    'SOT23_3': 'Package_TO_SOT_SMD:SOT-23',
    'Buffer': 'Package_SO:VSSOP-8_2.3x2mm_P0.5mm',
    'USB': 'Connector_USB:USB_Micro-B_GCT_USB3076-30-A',
    'R0402': 'Resistor_SMD:R_0402_1005Metric',
    'R0603': 'Resistor_SMD:R_0603_1608Metric',
    'C0402': 'Capacitor_SMD:C_0402_1005Metric',
    'C0603': 'Capacitor_SMD:C_0603_1608Metric',
    'Fuse': 'Fuse:Fuse_0805_2012Metric',
    'TVS': 'Diode_SMD:D_SOD-323',
    'Header4': 'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical',
    'Header2': 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',
    'ManualSwitch': 'Button_Switch_THT:SW_PUSH_6mm',
}


def part(ref, symbol, value, mpn, manufacturer, footprint, nets, schematic,
         placement=None, body=None, kind='component', source='', note=''):
    return dict(ref=ref, symbol=symbol, value=value, mpn=mpn,
                manufacturer=manufacturer, footprint=footprint,
                nets={str(k): v for k, v in nets.items()}, schematic=schematic,
                placement=placement, body=body, kind=kind, source=source, note=note)


def resistor(ref, value, mpn, nets, schematic, placement=None, package='R0402'):
    body = [1.05, 0.55, 0.4] if package == 'R0402' else [1.7, 0.9, 0.55]
    return part(ref, 'R', value, mpn, 'Yageo', package, nets, schematic,
                placement, body, source='https://www.yageo.com/en/Product/Index/Chip_Resistors')


def capacitor(ref, value, mpn, nets, schematic, placement=None, package='C0603'):
    body = [1.75, 0.95, 0.95] if package == 'C0603' else [1.05, 0.55, 0.6]
    return part(ref, 'C', value, mpn, 'Murata', package, nets, schematic,
                placement, body, source='https://www.murata.com/en-global/products/capacitor/mlcc')


GPIO_NETS = {23: 'LCD_DIN', 18: 'LCD_CLK', 21: 'LCD_CS', 22: 'LCD_DC',
             19: 'LCD_RST', 25: 'LCD_BL', 26: 'BTN_UP', 27: 'BTN_DOWN',
             32: 'BTN_LEFT', 33: 'BTN_RIGHT', 13: 'BTN_FIRE', 14: 'BTN_MENU'}

CARRIER = [
    part('J1', 'USB', 'Micro-B / power only', 'USB3076-30-A', 'GCT', 'USB',
         {1: 'VBUS', 2: None, 3: None, 4: None, 5: 'GND', 'SH': 'GND'},
         (25.4, 43.18), (12.35, 4.25, 'B', 0), [7.6, 5.75, 2.55],
         source='https://gct.co/connector/usb3076',
         note='PCB-edge datum used; mouth Y=0.30, rear Y=5.85. D+/D-/ID unconnected.'),
    part('F1', 'Fuse', '750mA PPTC', 'MF-PSMF075X-2', 'Bourns', 'Fuse',
         {1: 'VBUS', 2: 'VBUS_FUSED'}, (58.42, 30.48),
         (18.9, 5.8, 'B', 0), [2.3, 1.5, 1.25],
         source='https://www.bourns.com/docs/product-datasheets/mf-psmf.pdf'),
    part('D1', 'TVS', '5V bidirectional ESD', 'CDSOD323-T05C', 'Bourns', 'TVS',
         {1: 'GND', 2: 'VBUS_FUSED'}, (83.82, 35.56),
         (5.4, 4.1, 'B', 0), [2.70, 1.45, 1.14],
         source='https://www.bourns.com/docs/product-datasheets/cdsod323-txxc.pdf',
         note='ESD shunt, not a 5.5V overvoltage clamp. No system ESD qualification.'),
    part('U2', 'LDO', 'TLV75733PDBVR', 'TLV75733PDBVR', 'Texas Instruments', 'SOT23_5',
         {1: 'VBUS_FUSED', 2: 'GND', 3: 'VBUS_FUSED', 4: None, 5: '3V3'},
         (119.38, 35.56), (11.9, 11.7, 'F', 90), [1.75, 3.05, 1.45],
         source='https://www.ti.com/lit/ds/symlink/tlv757p.pdf',
         note='1A electrical rating; continuous current is thermally gated. EN tied to input.'),
    capacitor('C1', '10u / 10V X5R', 'GRM188R61A106KE69D', {1: 'VBUS_FUSED', 2: 'GND'},
              (157.48, 30.48), (17.0, 13.2, 'F', 0)),
    capacitor('C2', '10u / 10V X5R', 'GRM188R61A106KE69D', {1: '3V3', 2: 'GND'},
              (182.88, 30.48), (14.5, 12.8, 'F', 90)),
    capacitor('C3', '100n / 16V X7R', 'GRM155R71C104KA88D', {1: '3V3', 2: 'GND'},
              (208.28, 30.48), (21.75, 27.5, 'F', 90), 'C0402'),
    capacitor('C4', '1u / 10V X5R', 'GRM155R61A105KE15D', {1: 'EN', 2: 'GND'},
              (165.1, 93.98), (21.75, 25.2, 'F', 90), 'C0402'),
    resistor('R1', '10k / 1%', 'RC0402FR-0710KL', {1: '3V3', 2: 'EN'},
             (139.7, 93.98), (21.75, 22.6, 'F', 90)),
    resistor('R2', '10k / 1%', 'RC0402FR-0710KL', {1: '3V3', 2: 'BOOT'},
             (190.5, 93.98), (14.1, 8.1, 'F', 0)),
    resistor('R3', '10k / 1%', 'RC0402FR-0710KL', {1: 'STRAP_GPIO2', 2: 'GND'},
             (215.9, 93.98), (15.2, 10.7, 'F', 0)),
    resistor('R4', '10k / 1%', 'RC0402FR-0710KL', {1: 'STRAP_GPIO12', 2: 'GND'},
             (241.3, 93.98), (15.4, 9.5, 'F', 0)),
    part('U1', 'ESP32', 'ESP32-WROOM-32E-N4', 'ESP32-WROOM-32E-N4', 'Espressif', 'ESP32',
         {1: 'GND', 2: '3V3', 3: 'EN', 4: None, 5: None, 6: None, 7: None,
          8: 'BTN_LEFT', 9: 'BTN_RIGHT', 10: 'LCD_BL', 11: 'BTN_UP', 12: 'BTN_DOWN',
          13: 'BTN_MENU', 14: 'STRAP_GPIO12', 15: 'GND', 16: 'BTN_FIRE',
          17: None, 18: None, 19: None, 20: None, 21: None, 22: None, 23: None,
          24: 'STRAP_GPIO2', 25: 'BOOT', 26: None, 27: None, 28: None, 29: None,
          30: 'LCD_CLK', 31: 'LCD_RST', 32: None, 33: 'LCD_CS',
          34: 'UART_RX', 35: 'UART_TX', 36: 'LCD_DC', 37: 'LCD_DIN', 38: 'GND', 39: 'GND'},
         (58.42, 170.18), (12.0, 22.85, 'B', 0), [18.0, 25.5, 3.1],
         source='https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf',
         note='Radios off. Antenna over existing cutout; no RF performance claim.'),
    part('J2', 'LCD', 'LCD wire pads / 26117', 'PCB feature', 'Carrier fabricator', 'LCDPads',
         {1: '3V3', 2: 'GND', 3: 'LCD_DIN', 4: 'LCD_CLK', 5: 'LCD_CS',
          6: 'LCD_DC', 7: 'LCD_RST', 8: 'LCD_BL'}, (177.8, 223.52),
         (21.55, 16.3, 'F', 0), [0, 0, 0], kind='pcb_feature',
         source='https://www.waveshare.com/wiki/0.85inch_LCD_Module',
         note='Eight solder wires after MX1.25 removal. Physical module pad order requires sample confirmation.'),
    part('J3', 'Pogo', 'Pogo / 3V3 sense only', 'PCB feature', 'Carrier fabricator', 'PogoPads',
         {1: 'GND', 2: '3V3', 3: 'UART_TX', 4: 'UART_RX', 5: 'EN', 6: 'BOOT'},
         (254.0, 223.52), (12.0, 8.25, 'B', 0), [0, 0, 0], kind='pcb_feature',
         note='Device-centric TX/RX. Pad 2 is a sense output; never a supply input.'),
]

for index, (name, x, y) in enumerate([
        ('Up', 7.4, 11.5), ('Down', 7.4, 4.5), ('Left', 3.9, 8.0),
        ('Right', 10.9, 8.0), ('Fire', 18.6, 10.8), ('Menu', 18.0, 5.4)], 1):
    CARRIER.append(part('SW' + str(index), 'Switch', name + ' / 160gf',
                        '2337228-2', 'TE Connectivity', 'TESwitch',
                        {1: 'BTN_' + name.upper(), 2: 'GND'},
                        (139.7 + (index - 1) * 30.48, 157.48), (x, y, 'F', 0),
                        [3.6, 2.8, 0.85],
                        source='https://www.te.com/en/product-2337228-2.html',
                        note='Drawing B: T1/T2 common, T3/T4 common; 0.65 nominal height plus 0.20 general tolerance. Recommended plunger diameter 1.0mm.'))

FIXTURE = [
    part('J1', 'Pogo', 'Handheld contacts', 'Interface', 'Fixture fabricator', 'PogoPads',
         {1: 'GND', 2: 'SENSE_3V3', 3: 'DEVICE_TX', 4: 'DEVICE_RX', 5: 'DEVICE_EN', 6: 'DEVICE_BOOT'},
         (254.0, 175.26), kind='interface', note='Mating view; exact probe mechanics remain open.'),
    part('J2', 'Adapter', '3.3V UART adapter', 'TSW-104-07-G-S', 'Samtec', 'Header4',
         {1: None, 2: 'GND', 3: 'ADAPTER_TX', 4: 'ADAPTER_RX'}, (25.4, 175.26),
         source='https://www.samtec.com/products/tsw', note='Logical fixture header, not a universal adapter pinout. Pin 1/VCC intentionally NC.'),
    part('J3', 'PowerPort', 'Fixture local 3.3V', 'TSW-102-07-G-S', 'Samtec', 'Header2',
         {1: 'FX_3V3', 2: 'GND'}, (25.4, 35.56),
         source='https://www.samtec.com/products/tsw', note='Regulated 3.3V local fixture supply; no connection to SENSE_3V3.'),
    part('U1', 'Buffer', 'SN74LVC2G125DCUR', 'SN74LVC2G125DCUR', 'Texas Instruments', 'Buffer',
         {1: 'UART_OE_N', 2: 'ADAPTER_TX', 3: 'ADAPTER_RX', 4: 'GND',
          5: 'DEVICE_TX', 6: 'DEVICE_RX', 7: 'UART_OE_N', 8: 'FX_3V3'},
         [(1, 101.6, 175.26), (2, 177.8, 175.26), (3, 238.76, 40.64)],
         source='https://www.ti.com/lit/ds/symlink/sn74lvc2g125.pdf',
         note='Both channels gated; Ioff provides partial-power-down protection.'),
    part('U2', 'Comparator', 'TLV7041DBVR', 'TLV7041DBVR', 'Texas Instruments', 'SOT23_5',
         {1: 'UART_OE_N', 2: 'GND', 3: 'REF_HYS', 4: 'SENSE_DIV', 5: 'FX_3V3'},
         (172.72, 96.52), source='https://www.ti.com/lit/ds/symlink/tlv7041.pdf',
         note='Open drain; inputs tolerate 7V with supply off. Output low only when device rail is present; internal plus external hysteresis.'),
    part('D1', 'Reference', 'LM4040A20 / 2.048V', 'LM4040A20IDBZR', 'Texas Instruments', 'SOT23_3',
         {1: 'REF_2V048', 2: 'GND', 3: None}, (83.82, 63.5),
         source='https://www.ti.com/lit/ds/symlink/lm4040.pdf'),
    resistor('R1', '1k / 1%', 'RC0603FR-071KL', {1: 'FX_3V3', 2: 'REF_2V048'}, (58.42, 35.56), package='R0603'),
    resistor('R2', '523k / 1%', 'RC0402FR-07523KL', {1: 'SENSE_3V3', 2: 'SENSE_DIV'}, (119.38, 60.96)),
    resistor('R3', '1M / 1%', 'RC0402FR-071ML', {1: 'SENSE_DIV', 2: 'GND'}, (144.78, 60.96)),
    resistor('R4', '10k / 1%', 'RC0402FR-0710KL', {1: 'REF_2V048', 2: 'REF_HYS'}, (83.82, 106.68)),
    resistor('R5', '1M / 1%', 'RC0402FR-071ML', {1: 'UART_OE_N', 2: 'REF_HYS'}, (119.38, 106.68)),
    resistor('R6', '10k / 1%', 'RC0402FR-0710KL', {1: 'FX_3V3', 2: 'UART_OE_N'}, (210.82, 91.44)),
    resistor('R7', '1k / 1%', 'RC0603FR-071KL', {1: 'FX_3V3', 2: 'GND'}, (185.42, 35.56), package='R0603'),
    resistor('R8', '100k / 1%', 'RC0402FR-07100KL', {1: 'ADAPTER_TX', 2: 'GND'}, (101.6, 203.2)),
    resistor('R9', '100k / 1%', 'RC0402FR-07100KL', {1: 'DEVICE_TX', 2: 'GND'}, (139.7, 203.2)),
    capacitor('C1', '100n / 16V X7R', 'GRM155R71C104KA88D', {1: 'FX_3V3', 2: 'GND'}, (109.22, 35.56), package='C0402'),
    capacitor('C2', '100n / 16V X7R', 'GRM155R71C104KA88D', {1: 'FX_3V3', 2: 'GND'}, (144.78, 35.56), package='C0402'),
]
for ref, value, net, x in [('SW1', 'BOOT (hold)', 'DEVICE_BOOT', 177.8),
                            ('SW2', 'RESET (pulse)', 'DEVICE_EN', 238.76)]:
    FIXTURE.append(part(ref, 'Switch', value, 'B3F-1000', 'Omron', 'ManualSwitch',
                        {1: net, 2: 'GND'}, (x, 233.68),
                        source='https://components.omron.com/us-en/products/switches/B3F'))

SCHEMATICS = {
    'carrier': dict(parts=CARRIER, paper='A3', title='Especcy carrier - electrical and placement study',
        flags=[('VBUS_FUSED', 238.76, 30.48)],
        notes=[(12.7, 12.7, '5V INPUT / LDO - qualified power source, 1A adapter minimum'),
               (12.7, 76.2, 'SOT-23-5 continuous-load thermal acceptance is OPEN; current rating is not thermal proof.'),
               (127.0, 76.2, 'RESET / BOOT STRAPS'),
               (12.7, 119.38, 'ESP32-WROOM-32E-N4 / radios disabled'),
               (127.0, 134.62, 'SIX ACTIVE-LOW CONTROLS / firmware pull-ups and 10ms debounce'),
               (127.0, 190.5, 'LCD / POGO INTERFACES'),
               (127.0, 254.0, 'Pogo: 1 GND, 2 3V3_SENSE, 3 device TX, 4 device RX, 5 EN, 6 BOOT.'),
               (127.0, 261.62, 'Pad 2 is sensing only. Never inject fixture power. Eight LCD wires; BL drives onboard transistor.'),
               (12.7, 269.24, 'UNROUTED DESIGN STUDY - no fabrication release, no physical fit or thermal acceptance.')]),
    'fixture': dict(parts=FIXTURE, paper='A3', title='Especcy manual programming fixture - reference circuit',
        flags=[('FX_3V3', 279.4, 35.56), ('GND', 299.72, 35.56)],
        notes=[(12.7, 12.7, 'FIXTURE LOCAL SUPPLY / independent of the handheld sense pad'),
               (12.7, 81.28, 'DEVICE RAIL SENSE / open collector, positive hysteresis, UART disabled by default'),
               (12.7, 139.7, 'BOTH UART DIRECTIONS / 3.3V LOGIC / partial-power-down buffer'),
               (12.7, 215.9, 'MANUAL BOOTLOADER: hold BOOT, pulse RESET, connect esptool, then release BOOT.'),
               (12.7, 254.0, 'Micro-B powers handheld. Adapter VCC is NC. FX_3V3 is local fixture power, never the pogo sense net.'),
               (12.7, 261.62, 'Device rail absent: UART_OE_N high, both buffers high impedance. Manual switches only sink to GND.'),
               (12.7, 269.24, 'Reference schematic only. Fixture mechanics and all power/flash/recovery cases require bench tests.')]),
}
