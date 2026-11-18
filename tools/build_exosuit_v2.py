import os, math
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
OUT='assets/alex-exosuit.glb'; os.makedirs('assets',exist_ok=True)
S=trimesh.Scene()
M={
'carbon':PBRMaterial(name='Graphite flexible composite',baseColorFactor=[9,20,29,255],metallicFactor=.42,roughnessFactor=.48,emissiveFactor=[.002,.012,.02]),
'armor':PBRMaterial(name='Obsidian ceramic titanium',baseColorFactor=[22,30,39,255],metallicFactor=.88,roughnessFactor=.24,emissiveFactor=[.004,.016,.024]),
'edge':PBRMaterial(name='Machined titanium edges',baseColorFactor=[74,91,102,255],metallicFactor=.92,roughnessFactor=.22),
'cyan':PBRMaterial(name='Cyan photonic inlay',baseColorFactor=[25,194,226,255],metallicFactor=.42,roughnessFactor=.18,emissiveFactor=[.02,.48,.72]),
'magenta':PBRMaterial(name='Magenta status ceramic',baseColorFactor=[105,25,76,255],metallicFactor=.72,roughnessFactor=.24,emissiveFactor=[.28,.012,.12]),
'glass':PBRMaterial(name='Smoked optical glass',baseColorFactor=[2,17,28,255],metallicFactor=.7,roughnessFactor=.09,emissiveFactor=[.01,.17,.23]),
'rubber':PBRMaterial(name='Elastomer traction rubber',baseColorFactor=[5,9,13,255],metallicFactor=.05,roughnessFactor=.82)}
COUNT=0
def add(n,m,mat='armor'):
 global COUNT
 if m is None or len(m.faces)==0:return
 m.visual=trimesh.visual.TextureVisuals(material=M[mat]);S.add_geometry(m,node_name=n,geom_name=n);COUNT+=1
def ball(c,r,sub=2):
 m=trimesh.creation.icosphere(subdivisions=max(3,sub));m.apply_scale(r);m.apply_translation(c);return m
def cyl(a,b,r,sections=10):
 a=np.array(a,float);b=np.array(b,float);d=b-a;L=np.linalg.norm(d)
 if L<1e-7:return None
 m=trimesh.creation.cylinder(radius=r,height=L,sections=max(24,sections));m.apply_transform(trimesh.geometry.align_vectors([0,0,1],d));m.apply_translation((a+b)/2);return m
def loft(prof,seg=32):
 v=[];f=[]
 for y,rx,rz,cx,cz in prof:
  for i in range(seg):
   a=2*math.pi*i/seg;v.append([cx+rx*math.cos(a),y,cz+rz*math.sin(a)])
 for j in range(len(prof)-1):
  for i in range(seg):
   a=j*seg+i;b=j*seg+(i+1)%seg;c=(j+1)*seg+i;d=(j+1)*seg+(i+1)%seg;f.extend([[a,b,c],[b,d,c]])
 for i in range(1,seg-1):f.extend([[0,i+1,i],[(len(prof)-1)*seg,(len(prof)-1)*seg+i,(len(prof)-1)*seg+i+1]])
 return trimesh.Trimesh(vertices=v,faces=f,process=True)
def plate(c,w,h,d=.035,cut=.16,angle=0):
 x,y,z=c;k=min(w,h)*cut;p=[(-w/2+k,-h/2),(w/2-k,-h/2),(w/2,-h/2+k),(w/2,h/2-k),(w/2-k,h/2),(-w/2+k,h/2),(-w/2,h/2-k),(-w/2,-h/2+k)];n=len(p)
 v=np.vstack([np.c_[p,np.full(n,-d/2)],np.c_[p,np.full(n,d/2)]]);f=[]
 for i in range(1,n-1):f.extend([[0,i,i+1],[n,n+i+1,n+i]])
 for i in range(n):j=(i+1)%n;f.extend([[i,j,n+i],[j,n+j,n+i]])
 m=trimesh.Trimesh(vertices=v,faces=f,process=True);m.apply_translation(c)
 if angle:m.apply_transform(trimesh.transformations.rotation_matrix(angle,[0,0,1],point=c))
 return m
def cable(n,pts,r=.005,mat='edge'):
 for i,(a,b) in enumerate(zip(pts[:-1],pts[1:])):add(f'{n}_link_{i+1:02}',cyl(a,b,r,8),mat)
def bolt_ring(prefix,x,y,z,r=.009,count=6,mat='edge'):
 for i in range(count):
  a=2*math.pi*i/count;add(f'{prefix}_fastener_{i+1:02}',ball((x+r*math.cos(a),y+r*math.sin(a),z),(.004,.004,.003),1),mat)
def panel(prefix,c,w,h,mat='armor',accent=True,detail=3):
 x,y,z=c;add(prefix,plate(c,w,h,.045,.19),mat)
 for side in (-1,1):
  add(f'{prefix}_edge_{"L" if side<0 else "R"}',cyl((x+side*w*.43,y-h*.34,z+.027),(x+side*w*.43,y+h*.34,z+.027),.0035,6),'edge')
 if accent:
  add(prefix+'_lightguide',cyl((x-w*.27,y+h*.31,z+.03),(x+w*.27,y+h*.31,z+.03),.0038,8),'cyan')
 for j in range(detail):
  yy=y+(j-(detail-1)/2)*h*.13
  add(f'{prefix}_microvent_{j+1:02}',plate((x+w*.22,yy,z+.03),w*.19,h*.035,.009,.08), 'rubber')
 bolt_ring(prefix,x-w*.38,y-h*.34,z+.034);bolt_ring(prefix,x+w*.38,y-h*.34,z+.034)
def segment(prefix,center,radii,material='armor',rings=5):
 x,y,z=center;rx,ry,rz=radii
 add(prefix+'_shell',ball(center,(rx,ry,rz),2),material)
 for i in range(rings):
  yy=y-ry*.72+(i/(max(1,rings-1)))*ry*1.44
  for k in range(3):
   a=(k/3)*2*math.pi
   p1=(x+(rx+.004)*math.cos(a),yy,z+(rz+.004)*math.sin(a));p2=(x+(rx+.004)*math.cos(a+.65),yy,z+(rz+.004)*math.sin(a+.65))
   add(f'{prefix}_rib_{i+1:02}_{k+1}',cyl(p1,p2,.004,6),'edge')
def detail_grid(prefix,cx,cy,cz,w,h,cols,rows,mat='edge'):
 for row in range(rows):
  for col in range(cols):
   x=cx+(col-(cols-1)/2)*w/cols;y=cy+(row-(rows-1)/2)*h/rows
   add(f'{prefix}_tile_{row+1:02}_{col+1:02}',plate((x,y,cz),w/cols*.62,h/rows*.58,.008,.22),mat)
add('base_torso',loft([(.94,.17,.115,0,0),(1.04,.205,.13,0,0),(1.17,.205,.13,0,0),(1.30,.235,.145,0,0),(1.43,.285,.16,0,0),(1.54,.315,.155,0,0),(1.61,.255,.125,0,0)]),'carbon')
add('base_pelvis',loft([(.82,.16,.12,0,0),(.90,.22,.14,0,0),(1.00,.235,.145,0,0),(1.07,.19,.125,0,0)]),'carbon')
add('base_neck',loft([(1.57,.075,.075,0,0),(1.66,.078,.078,0,0),(1.72,.082,.08,0,0)]),'carbon')
add('base_head_skull',loft([(1.72,.075,.082,0,.005),(1.76,.105,.105,0,.005),(1.84,.118,.112,0,0),(1.92,.105,.105,0,-.002),(1.95,.07,.075,0,-.005)]),'carbon')
add('base_jaw',loft([(1.715,.055,.06,0,.025),(1.75,.082,.075,0,.02),(1.79,.09,.082,0,.012)]),'carbon')
for s,d in [(-1,'L'),(1,'R')]:
 add(f'base_ear_{d}',ball((s*.112,1.825,0),(.018,.035,.028),2),'carbon')
 add(f'base_upper_arm_{d}',loft([(1.19,.065,.07,s*.405,0),(1.28,.083,.082,s*.405,0),(1.40,.095,.09,s*.405,0),(1.51,.09,.085,s*.405,0)]),'carbon')
 add(f'base_forearm_{d}',loft([(.91,.055,.06,s*.435,.005),(.99,.067,.07,s*.435,.005),(1.10,.073,.073,s*.43,.005),(1.20,.068,.07,s*.425,.005)]),'carbon')
 add(f'base_hand_{d}',loft([(.79,.042,.032,s*.445,.02),(.83,.055,.04,s*.445,.02),(.90,.052,.042,s*.445,.01)]),'carbon')
 for i in range(4):
  xx=s*(.405+i*.023)
  add(f'base_finger_{d}_{i+1}',loft([(.685,.010,.011,xx,.025),(.72,.012,.013,xx,.025),(.77,.011,.012,xx,.025)]),'carbon')
 add(f'base_thumb_{d}',loft([(.75,.012,.013,s*.445,.03),(.79,.014,.014,s*.435,.03),(.83,.012,.012,s*.45,.025)]),'carbon')
 add(f'base_thigh_{d}',loft([(.48,.078,.082,s*.165,0),(.57,.103,.10,s*.17,0),(.73,.112,.11,s*.17,0),(.88,.105,.105,s*.16,0),(.98,.09,.09,s*.15,0)]),'carbon')
 add(f'base_shin_{d}',loft([(.12,.052,.06,s*.165,.005),(.20,.065,.07,s*.165,.005),(.34,.076,.078,s*.165,0),(.47,.07,.073,s*.165,0),(.54,.068,.07,s*.165,0)]),'carbon')
 add(f'base_foot_{d}',loft([(.045,.07,.135,s*.165,.095),(.075,.082,.15,s*.165,.10),(.13,.073,.12,s*.165,.055),(.19,.055,.08,s*.165,.015)]),'carbon')
add('helmet_shell',loft([(1.70,.105,.10,0,.005),(1.75,.135,.125,0,.005),(1.84,.145,.13,0,0),(1.92,.13,.12,0,-.005),(1.955,.09,.085,0,-.008)]),'armor')
add('helmet_crown',plate((0,1.94,.018),.205,.085,.045),'armor')
add('helmet_visor',plate((0,1.845,.124),.245,.075,.018,.10),'glass')
add('helmet_brow',plate((0,1.895,.137),.25,.026,.02),'edge')
add('helmet_jaw',plate((0,1.755,.105),.19,.07,.04),'armor')
for s,d in [(-1,'L'),(1,'R')]:
 add(f'helmet_cheek_{d}',plate((s*.105,1.79,.10),.075,.105,.04,.18,s*.12),'armor')
 add(f'helmet_temporal_{d}',ball((s*.137,1.84,0),(.025,.065,.075),2),'edge')
 add(f'helmet_sensor_{d}',ball((s*.15,1.85,.035),(.012,.018,.025),2),'cyan')
 add(f'helmet_audio_{d}',plate((s*.14,1.82,.025),.04,.06,.02),'magenta')
for i in range(7):
 x=(i-3)*.028;add(f'helmet_crown_ridge_{i+1:02}',cyl((x,1.925,.07),(x,1.955,.045),.0035,6),'edge')
add('collar',loft([(1.58,.13,.12,0,0),(1.63,.15,.13,0,0),(1.68,.12,.11,0,0)]),'armor')
for s,d in [(-1,'L'),(1,'R')]:
 add(f'collar_actuator_{d}',cyl((s*.105,1.59,-.03),(s*.12,1.67,-.02),.018,12),'edge')
for s,d in [(-1,'L'),(1,'R')]:
 panel(f'chest_{d}',(s*.155,1.445,.142),.285,.245,'armor',True,4)
 add(f'chest_clavicle_{d}',plate((s*.16,1.565,.105),.26,.065,.035,.18,s*.10),'edge')
 add(f'chest_lower_lobe_{d}',plate((s*.15,1.335,.155),.23,.07,.035,.15,s*.04),'armor')
 for j in range(5):
  add(f'chest_microchannel_{d}_{j+1}',cyl((s*.08,1.49-j*.022,.17),(s*.22,1.49-j*.022,.17),.0025,6),'edge')
 add(f'chest_side_intake_{d}',plate((s*.29,1.43,.08),.055,.14,.028,.18,s*.1),'rubber')
 detail_grid(f'chest_service_{d}',s*.155,1.44,.17,.12,.10,3,3,'edge')
add('sternum_spine',plate((0,1.44,.205),.085,.29,.055),'edge')
for i,yy in enumerate((1.515,1.455,1.395)):
 add(f'sternum_status_inlay_{i+1}',plate((0,yy,.239),.012,.026,.006,.12),'cyan')
add('back_plate',plate((0,1.43,-.145),.37,.39,.07),'armor')
add('back_spinal_housing',loft([(1.20,.055,.045,0,-.18),(1.42,.07,.05,0,-.19),(1.62,.06,.045,0,-.15)]),'armor')
for s,d in [(-1,'L'),(1,'R')]:
 panel(f'back_lateral_{d}',(s*.13,1.44,-.195),.13,.30,'armor',False,0)
 for i in range(8):add(f'back_vent_{d}_{i+1:02}',plate((s*.13,1.53-i*.027,-.225),.085,.012,.008),'rubber')
 add(f'back_thruster_mount_{d}',ball((s*.19,1.36,-.19),(.06,.11,.06),2),'edge')
 for i in range(4):add(f'back_thruster_fin_{d}_{i+1}',plate((s*(.19+i*.009),1.36,-.235),.018,.12,.012,.1),'armor')
for s,d in [(-1,'L'),(1,'R')]:
 add(f'shoulder_under_{d}',ball((s*.39,1.51,0),(.13,.13,.12),2),'carbon')
 panel(f'shoulder_{d}',(s*.405,1.535,.045),.255,.205,'armor',True,3)
 add(f'shoulder_cap_{d}',ball((s*.405,1.58,.045),(.115,.075,.105),2),'armor')
 for i in range(5):add(f'shoulder_scale_{d}_{i+1}',plate((s*(.32+i*.038),1.49,.12),.04,.09,.018,.18,s*.1),'edge')
 add(f'shoulder_status_{d}',cyl((s*.34,1.62,.11),(s*.47,1.62,.09),.005,8),'cyan')
 panel(f'upper_arm_{d}',(s*.405,1.335,.07),.15,.255,'armor',True,3)
 add(f'upper_arm_lateral_{d}',plate((s*.50,1.34,.005),.06,.22,.035,.18,s*.08),'edge')
 for i in range(4):add(f'upper_arm_rib_{d}_{i+1}',cyl((s*.37,1.25+i*.05,.09),(s*.46,1.25+i*.05,.09),.003,6),'edge')
 add(f'elbow_{d}',ball((s*.425,1.19,.025),(.075,.075,.075),2),'edge')
 add(f'elbow_cap_{d}',plate((s*.425,1.19,.095),.105,.10,.035),'armor')
 add(f'elbow_hinge_{d}',cyl((s*.425,1.15,-.01),(s*.425,1.23,-.01),.018,12),'edge')
 panel(f'forearm_{d}',(s*.435,1.015,.075),.17,.265,'armor',True,4)
 add(f'forearm_outer_rail_{d}',cyl((s*.50,1.13,.045),(s*.50,.90,.045),.012,8),'edge')
 add(f'forearm_inner_rail_{d}',cyl((s*.37,1.12,.08),(s*.38,.91,.08),.008,8),'magenta')
 for i in range(6):add(f'forearm_vent_{d}_{i+1}',plate((s*.49,.94+i*.027,.112),.09,.009,.006),'rubber')
 add(f'wrist_joint_{d}',ball((s*.445,.865,.02),(.047,.045,.045),2),'edge')
 add(f'hand_guard_{d}',plate((s*.445,.815,.075),.115,.10,.035),'armor')
 add(f'hand_dorsal_{d}',plate((s*.445,.83,.105),.075,.085,.018),'edge')
 for i in range(4):
  xx=s*(.40+i*.03)
  add(f'finger_armor_{d}_{i}',plate((xx,.745,.05),.022,.07,.018),'armor')
  add(f'finger_tip_{d}_{i}',ball((xx,.705,.05),(.011,.018,.012),1),'edge')
  add(f'finger_knuckle_{d}_{i}',ball((xx,.765,.07),(.013,.012,.012),1),'edge')
 add(f'thumb_{d}',cyl((s*.39,.81,.04),(s*.37,.755,.07),.014,8),'armor')
 add(f'palm_core_{d}',plate((s*.50,.78,.10),.075,.055,.018),'rubber')
for i,(yy,ww) in enumerate([(1.245,.30),(1.17,.295),(1.095,.285),(1.02,.27)]):
 panel(f'abdomen_segment_{i+1}',(0,yy,.13),ww,.066,'armor',True,2)
 for s,d in [(-1,'L'),(1,'R')]:add(f'abdomen_flex_{i+1}_{d}',ball((s*ww*.43,yy,.09),(.025,.045,.04),1),'rubber')
for s,d in [(-1,'L'),(1,'R')]:
 add(f'oblique_actuator_{d}',loft([(.99,.035,.035,s*.205,.01),(1.10,.04,.04,s*.22,.01),(1.22,.035,.035,s*.22,.01)]),'edge')
add('utility_belt',loft([(.94,.245,.155,0,0),(.985,.25,.16,0,0)]),'edge')
add('belt_buckle',plate((0,.965,.177),.13,.085,.035),'edge')
add('belt_buckle_core',plate((0,.965,.199),.075,.044,.012),'cyan')
for s,d in [(-1,'L'),(1,'R')]:
 for i in range(2):
  x=s*(.19+i*.07);prefix=f'belt_pouch_{d}_{i+1}'
  add(prefix,plate((x,.955,.14),.085,.14,.07),'armor')
  add(prefix+'_lid',plate((x,.99,.18),.08,.055,.025),'edge')
  add(prefix+'_latch',ball((x,.98,.198),(.012,.012,.008),1),'magenta')
  for j in range(3):add(f'{prefix}_molle_{j+1}',cyl((x-.025+j*.025,.925,.18),(x-.025+j*.025,.96,.18),.003,6),'edge')
 for i in range(3):
  x=s*(.34+i*.025);add(f'belt_cartridge_{d}_{i+1}',cyl((x,.94,.04),(x,.99,.04),.012,8),'edge')
 # Hip and thigh armor are self-contained; no exposed hanging thigh rods.
for s,d in [(-1,'L'),(1,'R')]:
 panel(f'hip_{d}',(s*.19,.88,.105),.20,.16,'armor',True,2)
 add(f'hip_lateral_{d}',plate((s*.275,.88,.01),.07,.18,.04,.18,s*.1),'edge')
 add(f'hip_hinge_{d}',ball((s*.17,.79,.01),(.045,.045,.045),2),'edge')
for s,d in [(-1,'L'),(1,'R')]:
 panel(f'thigh_{d}',(s*.17,.68,.095),.19,.34,'armor',True,4)
 add(f'thigh_lateral_{d}',plate((s*.275,.68,.005),.065,.29,.045,.18,s*.04),'edge')
 add(f'thigh_inner_{d}',plate((s*.11,.67,.15),.055,.24,.025),'armor')
 for i in range(7):add(f'thigh_groove_{d}_{i+1}',cyl((s*.12,.55+i*.037,.15),(s*.22,.55+i*.037,.15),.0025,6),'edge')
 add(f'knee_joint_{d}',ball((s*.17,.48,.09),(.073,.075,.07),2),'edge')
 add(f'knee_hinge_{d}',cyl((s*.17,.43,.02),(s*.17,.53,.02),.018,12),'edge')
 add(f'knee_cap_{d}',plate((s*.17,.48,.16),.145,.13,.045),'armor')
 add(f'knee_cap_inset_{d}',plate((s*.17,.48,.188),.075,.07,.014),'edge')
 for i in range(3):add(f'knee_louver_{d}_{i+1}',cyl((s*.22,.45+i*.025,.19),(s*.12,.45+i*.025,.19),.003,6),'cyan')
 panel(f'shin_{d}',(s*.17,.285,.105),.17,.30,'armor',True,4)
 add(f'shin_side_rail_{d}',cyl((s*.255,.42,.06),(s*.255,.14,.08),.012,8),'edge')
 for i in range(5):add(f'shin_vent_{d}_{i+1}',plate((s*.17,.20+i*.035,.14),.085,.009,.006),'rubber')
 add(f'ankle_joint_{d}',ball((s*.17,.12,.01),(.055,.06,.06),2),'edge')
 add(f'boot_{d}',loft([(.035,.085,.155,s*.17,.105),(.065,.095,.17,s*.17,.105),(.12,.09,.155,s*.17,.085),(.18,.073,.11,s*.17,.035),(.25,.067,.085,s*.17,.005)]),'armor')
 add(f'boot_outsole_{d}',loft([(.018,.102,.18,s*.17,.11),(.035,.105,.185,s*.17,.11)]),'rubber')
 add(f'boot_midsole_{d}',loft([(.035,.098,.18,s*.17,.11),(.052,.10,.18,s*.17,.11)]),'edge')
 add(f'boot_heel_{d}',plate((s*.17,.11,-.015),.12,.15,.075),'armor')
 add(f'boot_vamp_{d}',plate((s*.17,.12,.115),.145,.14,.055),'armor')
 add(f'boot_toe_{d}',ball((s*.17,.09,.235),(.09,.065,.10),2),'edge')
 add(f'boot_toe_cap_{d}',plate((s*.17,.105,.255),.14,.075,.025),'armor')
 add(f'boot_cuff_{d}',loft([(.21,.075,.085,s*.17,.005),(.25,.085,.095,s*.17,.005),(.29,.078,.09,s*.17,.005),(.31,.07,.08,s*.17,.005)]),'edge')
 add(f'boot_gaiter_{d}',plate((s*.17,.235,.08),.11,.10,.03),'armor')
 for i in range(6):
  y=.15+i*.018
  add(f'boot_eyelet_{d}_{i+1}',ball((s*.17+(.045 if i%2==0 else -.045),y,.155),(.008,.008,.006),1),'edge')
  add(f'boot_lace_{d}_{i+1}',cyl((s*.17-.045,y,.16),(s*.17+.045,y-.009,.16),.0028,6),'cyan')
 for row in range(5):
  for col in range(3):
   x=s*.17+(col-1)*.052;z=.02+row*.043
   add(f'boot_tread_{d}_{row+1}_{col+1}',plate((x,.014,z),.035,.026,.009,.12),'rubber')
for side,d in [(-1,'L'),(1,'R')]:
 for region,y0,x0 in [('arm',1.34,.415),('bracer',1.02,.49),('thigh',.68,.17),('shin',.28,.17)]:
  for row in range(5):
   for col in range(4):
    x=side*(x0+(col-1.5)*.022);y=y0+(row-2)*.045;z=.155 if region in ('thigh','shin') else .13
    add(f'{region}_microbolt_{d}_{row+1:02}_{col+1:02}',ball((x,y,z),(.004,.004,.003),1),'edge')
 for region,cx,cy,cz,w,h in [('shoulder',.405,1.535,.09,.18,.13),('forearm',.49,1.01,.12,.12,.19),('thigh',.17,.68,.15,.13,.25),('shin',.17,.285,.15,.11,.22)]:
  for row in range(5):
   for col in range(3):
    x=side*(cx+(col-1)*w/3);y=cy+(row-2)*h/5
    add(f'{region}_segmented_inlay_{d}_{row+1:02}_{col+1:02}',plate((x,y,cz),w/3*.55,h/5*.52,.006,.18),('edge' if region in ('thigh','shin') else ('edge' if (row+col)%3 else 'magenta')))
for i in range(18):
 y=1.20+i*.022
 add(f'dorsal_spine_link_{i+1:02}',plate((0,y,-.205),.055,.018,.012),'edge')
 add(f'dorsal_spine_light_{i+1:02}',cyl((-.018,y,-.214),(.018,y,-.214),.0025,6),'cyan')
for i in range(12):
 x=(i-5.5)*.025
 add(f'sternum_rivet_{i+1:02}',ball((x,1.44,.24),(.004,.004,.003),1),'edge')
for s,d in [(-1,'L'),(1,'R')]:
 cable(f'shoulder_cable_{d}',[(s*.30,1.55,-.08),(s*.36,1.43,-.09),(s*.40,1.30,-.08)],.005,'edge')
bounds=S.bounds
height=float(bounds[1,1]-bounds[0,1])
scale_y=1.8/height
T=np.eye(4);T[1,1]=scale_y;T[1,3]=-float(bounds[0,1])*scale_y
S.apply_transform(T)
S.export(OUT)
print('Created',OUT,'height_m',round(float(S.bounds[1,1]-S.bounds[0,1]),6),'named_mesh_nodes',COUNT,'scene_nodes',len(S.graph.nodes),'bytes',os.path.getsize(OUT))
