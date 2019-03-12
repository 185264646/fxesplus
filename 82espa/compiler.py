#!/usr/bin/python3
import sys,os
os.chdir(os.path.dirname(__file__))
sys.path.append('..')
from libcompiler import (
		set_font, set_npress_array, get_disassembly, get_commands,
		read_rename_list, set_byte_to_key_dict,
		to_font,
		process_program
		)

get_disassembly('disas.txt')
get_commands('gadgets')
read_rename_list('labels')


# NOTE: probably incorrect. just copied from 570es+ font file.
font=[*''' ¿àáéíóöüú¡Ó¿................... !"#×%÷'()⋅+,—./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[▫]^_-abcdefghijklmnopqrstuvwxyz{|}~ 𝐢𝐞×⏨∞°ʳᵍ∠''',
		'x̅','y̅','x̂',
		*'ŷ→↲⇒ₓ⏨','⏨̄',
		*'⌟≤≠≥◢√∫ᴀʙᴄₙ▶◀⁰¹²³⁴⁵⁶⁷⁸⁹',
		'⁻¹','ˣ','¹⁰',
		*'₍₎±₀₁₂₋ꜰɴᴘµ𝐀𝐁𝐂𝐃𝐄𝐅𝐏▷Σαγεθλμπσϕℓℏ█⎕₃▂................................................''']

assert '⁻¹'==font[0xAA]
assert len(font)==0x100,len(font)
set_font(font)


# NOTE: may be incorrect
npress=(
	999,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,
	4  ,4  ,4  ,4  ,4  ,4  ,4  ,4  ,4  ,100,100,100,100,100,100,100,
	100,102,100,100,100,2  ,100,100,1  ,1  ,100,1  ,1  ,1  ,1  ,100,
	1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,2  ,100,100,100,100,100,
	100,2  ,2  ,2  ,2  ,2  ,2  ,100,100,100,100,100,100,100,1  ,1  ,
	100,100,100,100,2  ,100,100,2  ,2  ,2  ,100,100,1  ,100,1  ,100,
	1  ,100,100,2  ,100,100,100,100,1  ,2  ,1  ,2  ,2  ,2  ,100,100,
	2  ,2  ,2  ,2  ,1  ,1  ,2  ,1  ,100,100,100,100,100,100,100,100,
	100,2  ,2  ,100,100,3  ,3  ,3  ,100,100,100,1  ,2  ,100,100,100,
	2  ,2  ,2  ,2  ,100,100,100,100,1  ,100,100,100,100,100,100,2  ,
	1  ,1  ,1  ,1  ,100,100,100,100,2  ,100,100,100,100,100,1  ,100,
	2  ,2  ,2  ,2  ,100,100,100,100,100,100,100,100,100,100,2  ,2  ,
	100,100,2  ,100,100,100,100,100,100,100,100,100,100,100,100,100,
	100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,
	100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,
	100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,
	)  # the box may be harder to manipulate
set_npress_array(npress)

def get_binary(filename):
	file = open(filename, 'rb')
	result = file.read()
	file.close()
	return result
rom = get_binary('rom.bin')

def get_symbols(rom):
	symbols = [''] * 256
	for i in range(1, 256):
		ptr_adr = 0x148E + 2*i  # referenced at code address 02BBE
		ptr = rom[ptr_adr+1] << 8 | rom[ptr_adr]

		info = rom[0x168E + i]
		symbol_len = info & 0xF
		symbol_type = info >> 4 # if 15 then func else normal

		if symbol_type != 15: ptr += symbol_type

		result = to_font(rom[ptr:ptr+symbol_len])
		if symbol_type == 15: result = result + '('
		symbols[i] = result

	return symbols
symbols = get_symbols(rom)

def to_key(byte):
	if byte==0:
		return '<NUL>'

	offset=0
	sym=symbols[byte]
	while npress[byte]>=100: byte-=1; offset+=1
	if offset==0:
		return sym
	else:
		return f'<{sym}:{symbols[byte]}+{offset}>'

set_byte_to_key_dict({i: to_key(i) for i in range(256)})

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--target', default='overflow',
		choices=('none', 'overflow', 'loader'),
		help='how will the output be used')
parser.add_argument('-f', '--format', default='key',
		choices=('hex', 'key'),
		help='output format')
args = parser.parse_args()

program = sys.stdin.read().split('\n')

process_program(args, program, overflow_initial_sp=0x8DAE)