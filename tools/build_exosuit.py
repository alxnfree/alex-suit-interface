import os, math
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
OUT='assets/alex-exosuit.glb'; os.makedirs('assets',exist_ok=True)
S=trimesh.Scene()
M={
'carbon':PBRMaterial(name='Graphite undersuit',baseColorFactor=[12,29,39,255],metallicFactor=.48,roughnessFactor=.42,emissiveFactor=[.005,.035,.05]),
'armor':PBRMaterial(name='Obsidian ceramic titanium',baseColorFactor=[19,27,36,255],metallicFactor=.9,roughnessFactor=.25,emissiveFactor=[.004,.018,.028]),
'cyan':PBRMaterial(name='Cyan photonic inlay',baseColorFactor=[20,200,232,255],metallicFactor=.5,roughnessFactor=.19,emissiveFactor=[.02,.45,.68]),
'magenta':PBRMaterial(name='Magenta status ceramic',baseColorFactor=[75,22,63,255],metallicFactor=.7,roughnessFactor=.26,emissiveFactor=[.22,.012,.11]),
'glass':PBRMaterial(name='Smoked visor glass',baseColorFactor=[3,21,32,255],metallicFactor=.72,roughnessFactor=.1,emissiveFactor=[.01,.16,.22]),
'metal':PBRMaterial(name='Titanium hardware',baseColorFactor=[95,91,78,255],metallicFactor=.88,roughnessFactor=.28)}
def add(n,parts,mat='armor'):
 parts=[p for p in parts if p is not None and len(p.faces)]
 if not parts:return
 g=trimesh.util.concatenate(parts);g.visual=trimesh.visual.TextureVisuals(material=M[mat]);S.add_geometry(g,node_name=n,geom_name=n)
def loft(prof,seg=16):
 v=[];f=[]
 for y,rx,rz,cx,cz in prof:
  for i in range(seg):
   a=2*math.pi*i/seg;v.append([cx+rx*math.cos(a),y,cz+rz*math.sin(a)])
 for j in range(len(prof)-1):
  for i in range(seg):
   a=j*seg+i;b=j*seg+(i+1)%seg;c=(j+1)*seg+i;d=(j+1)*seg+(i+1)%seg;f.extend([[a,b,c],[b,d,c]])
 for i in range(1,seg-1):f.extend([[0,i+1,i],[(len(prof)-1)*seg,(len(prof)-1)*seg+i,(len(prof)-1)*seg+i+1]])
 return trimesh.Trimesh(vertices=v,faces=f,process=True)
def ball(c,r,sub=1):
 m=trimesh.creation.icosphere(subdivisions=sub);m.apply_scale(r);m.apply_translation(c);return m
def bar(a,b,r=.009):
 a=np.array(a,float);b=np.array(b,float);d=b-a;L=np.linalg.norm(d)
 if L<1e-6:return None
 m=trimesh.creation.cylinder(radius=r,height=L,sections=6);m.apply_transform(trimesh.geometry.align_vectors([0,0,1],d));m.apply_translation((a+b)/2);return m
def cable(points,r=.008):
 q=[bar(a,b,r) for a,b in zip(points[:-1],points[1:])];q += [ball(p,[r,r,r],1) for p in points];return trimesh.util.concatenate([x for x in q if x])
def plate(c,size,depth=.045,cut=.18,ang=0):
 x,y,z=c;w,h=size;k=min(w,h)*cut
 p=[(-w/2+k,-h/2),(w/2-k,-h/2),(w/2,-h/2+k),(w/2,h/2-k),(w/2-k,h/2),(-w/2+k,h/2),(-w/2,h/2-k),(-w/2,-h/2+k)];n=len(p)
 v=np.vstack([np.c_[p,np.full(n,-depth/2)],np.c_[p,np.full(n,depth/2)]]);f=[]
 for i in range(1,n-1):f.extend([[0,i,i+1],[n,n+i+1,n+i]])
 for i in range(n):j=(i+1)%n;f.extend([[i,j,n+i],[j,n+j,n+i]])
 m=trimesh.Trimesh(vertices=v,faces=f,process=True);m.apply_translation(c)
 if ang:m.apply_transform(trimesh.transformations.rotation_matrix(ang,[0,0,1],point=c))
 return m
def armor(n,c,size,accent='cyan',ang=0):
 x,y,z=c;w,h=size
 parts=[plate(c,size,.05,.2,ang),cable([(x-w*.32,y+h*.29,z+.035),(x-w*.18,y+h*.35,z+.035),(x+w*.24,y+h*.35,z+.035)],.006),cable([(x-w*.30,y-h*.28,z+.035),(x+w*.28,y-h*.28,z+.035)],.005)]
 for s in [-1,1]:parts.append(ball((x+s*w*.36,y+h*.29,z+.04),[.01,.01,.008]))
 add(n,parts)
 if accent:add(n+'_light',[cable([(x-w*.27,y+h*.29,z+.043),(x+w*.25,y+h*.29,z+.043)],.005)],accent)
# Exposed articulated undersuit, shaped as a continuous athletic human silhouette
add('base_torso',[loft([(.66,.17,.12,0,0),(.83,.21,.14,0,0),(1.02,.20,.13,0,0),(1.19,.23,.15,0,0),(1.37,.29,.17,0,0),(1.51,.34,.17,0,0),(1.61,.28,.14,0,0)])],'carbon')
add('base_pelvis',[loft([(.54,.18,.13,0,0),(.66,.24,.15,0,0),(.80,.21,.14,0,0),(.87,.16,.12,0,0)])],'carbon')
add('base_neck',[loft([(1.58,.095,.09,0,0),(1.70,.09,.09,0,0),(1.77,.10,.10,0,0)])],'carbon');add('base_head',[ball((0,1.88,0),(.12,.16,.11),2)],'carbon')
for s,d in [(-1,'L'),(1,'R')]:
 add('base_upper_arm_'+d,[loft([(1.18,.07,.07,s*.39,0),(1.30,.09,.085,s*.42,0),(1.46,.095,.09,s*.42,0),(1.55,.09,.085,s*.40,0)])],'carbon')
 add('base_forearm_'+d,[loft([(.92,.06,.06,s*.48,.01),(1.03,.073,.07,s*.48,.01),(1.17,.07,.07,s*.47,.01),(1.27,.065,.065,s*.45,.01)])],'carbon')
 add('base_hand_'+d,[ball((s*.49,.86,.03),(.06,.08,.045))],'carbon')
 for i in range(4):
  xx=s*(.445+i*.03);add('base_finger_'+d+'_'+str(i),[loft([(.76,.011,.012,xx,0),(.81,.013,.013,xx,0),(.86,.012,.012,xx,0)])],'carbon')
 add('base_thigh_'+d,[loft([(.30,.09,.095,s*.17,0),(.41,.115,.11,s*.17,0),(.59,.115,.115,s*.18,0),(.72,.10,.095,s*.17,0)])],'carbon')
 add('base_shin_'+d,[loft([(.08,.06,.065,s*.17,.01),(.17,.08,.08,s*.17,.01),(.30,.08,.075,s*.17,.01),(.39,.075,.075,s*.17,.01)])],'carbon')
 add('base_foot_'+d,[loft([(.035,.07,.13,s*.17,.09),(.07,.08,.15,s*.17,.10),(.13,.07,.12,s*.17,.05)])],'carbon')
# Head, neck, torso and back assembly
armor('helmet_shell',(0,1.88,.045),(.285,.34));add('helmet_crown',[plate((0,2.035,.06),(.21,.095),.06)],'armor');add('helmet_visor',[plate((0,1.91,.112),(.235,.105),.025)],'glass');add('helmet_jaw',[plate((0,1.775,.10),(.20,.075),.045)],'armor')
for s,d in [(-1,'L'),(1,'R')]:add('helmet_temporal_'+d,[ball((s*.145,1.88,0),(.04,.07,.09)),cable([(s*.17,1.91,.01),(s*.19,1.88,.025),(s*.17,1.84,.01)],.008)],'metal')
add('collar',[loft([(1.62,.15,.14,0,0),(1.68,.16,.145,0,0),(1.73,.12,.115,0,0)])])
armor('chest_left',(-.155,1.43,.145),(.30,.30),ang=-.08);armor('chest_right',(.155,1.43,.145),(.30,.30),ang=.08)
add('sternum_spine',[plate((0,1.42,.205),(.095,.30),.055),cable([(0,1.53,.24),(0,1.43,.245),(0,1.31,.24)],.012)])
add('reactor_core',[trimesh.creation.cylinder(radius=.052,height=.022,sections=12)],'cyan');S.graph.update(frame_to='reactor_core',matrix=trimesh.transformations.translation_matrix([0,1.43,.25]))
armor('back_plate',(0,1.42,-.15),(.40,.43));add('dorsal_spine',[loft([(1.17,.05,.04,0,-.18),(1.39,.055,.045,0,-.19),(1.61,.05,.04,0,-.17)])])
# Full arms, gloves, fingers and shoulder articulation
for s,d in [(-1,'L'),(1,'R')]:
 armor('shoulder_'+d,(s*.42,1.49,.015),(.25,.22),'magenta',s*.12);add('shoulder_under_'+d,[ball((s*.42,1.47,0),(.13,.13,.12))])
 armor('upper_arm_'+d,(s*.435,1.30,.055),(.17,.28));add('elbow_'+d,[ball((s*.47,1.115,.025),(.085,.075,.085)),cable([(s*.40,1.12,.11),(s*.47,1.10,.13),(s*.54,1.12,.11)],.012)],'metal')
 armor('forearm_'+d,(s*.48,.99,.075),(.19,.27));add('forearm_ridge_'+d,[cable([(s*.42,1.10,.12),(s*.48,1.04,.16),(s*.55,.91,.12)],.012)],'magenta')
 add('hand_guard_'+d,[plate((s*.49,.84,.085),(.13,.12),.045)]);add('hand_dorsal_'+d,[cable([(s*.49,.89,.13),(s*.49,.84,.15),(s*.49,.80,.13)],.012)],'cyan')
 for i in range(4):
  xx=s*(.445+i*.03);add('finger_armor_'+d+'_'+str(i),[plate((xx,.785,.05),(.024,.10),.025),ball((xx,.76,.055),(.012,.014,.014))])
 add('thumb_'+d,[cable([(s*.43,.85,.04),(s*.405,.82,.075),(s*.40,.78,.08)],.014)])
# Segmented abdomen, belt with four utility pouches and thigh rigs
for i,(yy,ww) in enumerate([(1.17,.34),(1.08,.32),(.99,.29)]):add('abdomen_segment_'+str(i),[plate((0,yy,.13),(ww,.085),.035)]);add('abdomen_light_'+str(i),[cable([(-ww*.28,yy+.025,.155),(ww*.28,yy+.025,.155)],.004)],'cyan')
add('utility_belt',[loft([(.88,.255,.17,0,0),(.94,.26,.175,0,0)])]);add('belt_buckle',[plate((0,.91,.19),(.12,.09),.04),plate((0,.91,.215),(.065,.045),.012)],'metal')
for s,d in [(-1,'L'),(1,'R')]:
 for i in range(2):
  x=s*(.22+i*.075);add('belt_pouch_'+d+'_'+str(i),[plate((x,.91,.12),(.09,.13),.065),cable([(x-.03,.96,.16),(x+.03,.96,.16)],.006)])
 add('thigh_rig_'+d,[cable([(s*.22,.85,.06),(s*.25,.78,.07),(s*.25,.70,.07)],.012),plate((s*.25,.69,.09),(.11,.12),.04)],'metal')
armor('hip_L',(-.17,.77,.11),(.21,.18),'magenta',-.08);armor('hip_R',(.17,.77,.11),(.21,.18),'magenta',.08)
# Leg armor and complete tactical boots: heel counter, instep, toe cap, cuff and tread
for s,d in [(-1,'L'),(1,'R')]:
 armor('thigh_'+d,(s*.17,.53,.095),(.205,.31));add('thigh_lateral_'+d,[plate((s*.275,.53,.005),(.07,.25),.05,.25,s*.05)])
 add('knee_joint_'+d,[ball((s*.17,.365,.10),(.095,.095,.065)),plate((s*.17,.37,.16),(.16,.15),.05)],'metal');add('knee_cap_'+d,[plate((s*.17,.37,.19),(.13,.12),.035)])
 armor('shin_'+d,(s*.17,.205,.10),(.18,.27));add('shin_side_rail_'+d,[cable([(s*.26,.31,.07),(s*.27,.20,.08),(s*.24,.08,.10)],.013)],'metal')
 add('boot_'+d,[loft([(.035,.09,.16,s*.17,.12),(.07,.105,.18,s*.17,.12),(.13,.095,.16,s*.17,.10),(.19,.08,.105,s*.17,.04),(.27,.075,.085,s*.17,.01)])])
 add('boot_cuff_'+d,[loft([(.22,.085,.09,s*.17,.01),(.27,.09,.10,s*.17,.01),(.30,.075,.085,s*.17,.01)])],'metal')
 add('boot_heel_'+d,[plate((s*.17,.10,-.005),(.14,.16),.09)]);add('boot_vamp_'+d,[plate((s*.17,.095,.13),(.16,.18),.07)]);add('boot_toe_'+d,[ball((s*.17,.085,.245),(.095,.075,.12))])
 add('boot_outsole_'+d,[loft([(.025,.105,.18,s*.17,.12),(.045,.11,.185,s*.17,.12)])],'metal')
 add('boot_lacing_'+d,[cable([(s*.22,.17,.17),(s*.17,.19,.19),(s*.12,.17,.17)],.006),cable([(s*.22,.14,.17),(s*.17,.16,.19),(s*.12,.14,.17)],.006)],'cyan')
for s,d in [(-1,'L'),(1,'R')]:add('shoulder_status_'+d,[cable([(s*.35,1.57,.10),(s*.43,1.59,.10),(s*.51,1.55,.08)],.008)],'cyan')
S.export(OUT);print('Created',OUT,'nodes',len(S.graph.nodes),'bytes',os.path.getsize(OUT))
