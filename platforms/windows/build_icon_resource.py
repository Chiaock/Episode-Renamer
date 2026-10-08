from pathlib import Path
import struct
ico=Path('assets/icon.ico').read_bytes()
w,h,c,r,planes,bits,size,off=struct.unpack_from('<BBBBHHII',ico,6)
png=ico[off:off+size]
group=struct.pack('<HHH',0,1,1)+struct.pack('<BBBBHHIH',w,h,c,0,planes,bits,size,1)
b=bytearray(160)
def directory(o,n): struct.pack_into('<IIHHHH',b,o,0,0,0,0,0,n)
def entry(o,i,t,d): struct.pack_into('<II',b,o,i,t|(0x80000000 if d else 0))
directory(0,2);entry(16,3,32,True);entry(24,14,80,True)
directory(32,1);entry(48,1,56,True);directory(56,1);entry(72,1033,128,False)
directory(80,1);entry(96,1,104,True);directory(104,1);entry(120,1033,144,False)
relocations=[]
for e,p in [(128,png),(144,group)]:
    while len(b)%4: b.append(0)
    struct.pack_into('<IIII',b,e,len(b),len(p),0,0)
    relocations.append(e);b.extend(p)
raw=60;reloc=raw+len(b);sym=reloc+10*len(relocations)
header=struct.pack('<HHIIIHH',0x8664,1,0,sym,1,0,0)
section=struct.pack('<8sIIIIIIHHI',b'.rsrc\0\0\0',0,0,len(b),raw,reloc,0,len(relocations),0,0x40000040)
relocs=b''.join(struct.pack('<IIH',x,0,3) for x in relocations)
symbol=struct.pack('<8sIhHBB',b'.rsrc\0\0\0',0,1,0,3,0)
Path('icon_windows_amd64.syso').write_bytes(header+section+b+relocs+symbol+struct.pack('<I',4))
print('Embedded orange Windows icon resource.')
