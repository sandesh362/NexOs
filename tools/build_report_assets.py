"""Create original, clearly labelled interface concepts for the project report."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'report' / 'images'
OUT.mkdir(parents=True, exist_ok=True)
INK = '#172B40'
MUTED = '#4D6072'
LINE = '#CFD9E2'
BLUE = '#1E4D70'

def font(size, bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/' + ('arialbd.ttf' if bold else 'arial.ttf'), size)

def base(title):
    im = Image.new('RGB', (1600, 1000), '#F2F5F8')
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20,20,1580,980), 15, fill='white', outline=LINE, width=2)
    d.rectangle((21,21,1579,92),fill=INK)
    d.text((50,43),'NEXOS',font=font(28,True),fill='white')
    d.text((240,45),title,font=font(23),fill='white')
    d.text((1160,46),'INTERFACE CONCEPT',font=font(21,True),fill='#D5E5F1')
    d.rectangle((22,93,260,920),fill='#EAF0F5')
    for y,text in [(130,'Workspace'),(205,'Task history'),(280,'Granted folders'),(355,'Connections'),(430,'Settings')]:
        d.text((48,y),text,font=font(23,text=='Workspace'),fill=INK)
    d.text((50,870),'Local workstation',font=font(20),fill=MUTED)
    d.line((21,920,1579,920),fill=LINE,width=2)
    d.text((45,942),'Proposed Qt interface. Illustrative data; not an implemented application screenshot.',font=font(23),fill=MUTED)
    return im,d

def button(d,xy,text,primary=False):
    d.rounded_rectangle(xy,7,fill=BLUE if primary else 'white',outline=BLUE,width=2)
    f=font(23,True)
    b=d.textbbox((0,0),text,font=f)
    d.text(((xy[0]+xy[2]-(b[2]-b[0]))/2,xy[1]+17),text,font=f,fill='white' if primary else BLUE)

im,d=base('Task workspace')
d.text((305,125),'Inspect a development project',font=font(34,True),fill=INK)
d.text((305,183),'Read selected manifests and save a verified diagnosis report.',font=font(24),fill=MUTED)
d.rounded_rectangle((305,235,1535,347),9,fill='#F4F7FA',outline=LINE,width=2)
d.text((330,254),'GRANTED SCOPE',font=font(19,True),fill=MUTED)
d.text((330,288),'Read  /home/demo/projects/api     |     Create  /home/demo/reports',font=font(24),fill=INK)
d.text((305,390),'Execution stages',font=font(27,True),fill=INK)
for j,(t,s) in enumerate([
    ('Inspect supported manifests','Completed'),('Create a new report','Completed'),('Check report and source evidence','Verified')]):
    y=446+j*82
    d.ellipse((310,y,347,y+37),fill=BLUE)
    d.text((321,y+5),str(j+1),font=font(22,True),fill='white')
    d.text((365,y+3),t,font=font(25),fill=INK)
    d.text((1315,y+4),s,font=font(23,True),fill=BLUE)
d.line((305,705,1535,705),fill=LINE,width=2)
d.text((305,735),'Evidence',font=font(27,True),fill=INK)
d.text((305,780),'Report identity checked  /  Source digests unchanged  /  Task recorded',font=font(23),fill=MUTED)
button(d,(305,831,535,894),'Open report',True)
button(d,(560,831,810,894),'View task record')
im.save(OUT/'ui-task-workspace.png')

im,d=base('Review an external action')
d.text((305,125),'Create a project review event',font=font(34,True),fill=INK)
d.text((305,180),'Review the exact details before the connector creates the event.',font=font(24),fill=MUTED)
rows=[('Calendar','Project demo calendar'),('Title','NEXOS project review'),('When','20 October 2026, 5:00 PM to 5:30 PM'),('Timezone','Asia/Kolkata (UTC +05:30)'),('Attendees','member1@example.com, member2@example.com'),('Conference','Request a Google Meet link'),('Notifications','Send invitations to the two listed attendees')]
for j,(label,value) in enumerate(rows):
    y=245+j*70
    d.text((310,y),label,font=font(24,True),fill=INK)
    d.text((555,y),value,font=font(24),fill=INK)
    d.line((305,y+48,1530,y+48),fill=LINE,width=1)
d.text((310,752),'Approval applies only to these details. Changes require a new review.',font=font(23),fill=MUTED)
button(d,(305,822,500,888),'Cancel')
button(d,(525,822,760,888),'Edit details')
button(d,(1105,822,1530,888),'Approve and create event',True)
im.save(OUT/'ui-action-preview.png')
print('Created two report interface concepts.')
