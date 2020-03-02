# Quick render

Blender addon - Render and save view/cam in one click

**[Download latest](https://github.com/Pullusb/Quick_render/archive/master.zip)**

Want to support ? [Check out how](http://www.samuelbernou.fr/donate)

---

# Description

The goal is simple : Be able to export view snapshots in 3D view and iterate quickly.  
Press a button and it's exported, you didn't name anything ? fine, you can but don't have to.  
  

#### First use case exemple:  
You have the realisator/client/bossman/whatever behind you, guiding your navigation in the scene to extract some references views.  

BOSS: This point of view is nice can you export the..  
YOU: \[_click_\] Done.  
BOSS: huuu ok... \[_Look at you navigating..._\] Stop ! This view is cool too mayb..  
YOU: \[_click_\] Done !  
BOSS: ...and this slight different angle is...  
YOU: \[_click_\] Dooone !!  
BOSS: \[_suspicious_\] What ?! huuu ooooookaay... you sure ?  
YOU: \[_click (showing exported file)_\] Yep, there.  
BOSS: \[_whispering to himself_\] Wow that was way too fast ! What a pro, I admire him so much, lets make HIM the boss, oh yeah !  
YOU: \[_Getting a big head_\] Yup... thats me ! (hint: this last line totally breaks the hype... Trust me).  
  
#### Second use case (solo):  
You: \[_thinking nervously_\] I need this render out now !... Quick ! I'll have to press F12 then Alt+S, navigate to saving location (probably aside blend file !) then choose a name and Oh wait!...  
it's done.


### options details: 

**Save folder** : If not specified, create a 'quick_render' directory aside blend location and export inside

**Filename** : If not specified get a placeholder name like 'view_01' (placeholder can be customised in addon preference).  

Image will never be overwritten, always save while auto incrementing name 
You can use padding number like "my-beloved-cube_###", if not specified, automatic padding is 2 digits

Exemples with name : beloved-cube

**insert date** : beloved-cube\_2020-02-11\_20-35-46 (date format can be customised in addon preference)

**insert frame**: beloved-cube\_f0250

**Both** : beloved-cube\_2020-02-11\_20-35-46\_f0250 (starting to get confusing)

**open export directory** : Well... it open's it.

The button render view create a camera at current view before render to make a "real" render


## Todo:

- Check if already in a cam view for view render (create a camera overlapping with current camera)

- When user use his own padding '####' in name, behavior is different with date/frame infos insertion. Check how to make this consistent

---

## changelog:

2020-03-03 (1,1,0):  
- new button to make a "true" render from view (Create a cam with same name as the file cans place it in a "quick_cams" collections)
    - opt for later : "only cam" or "no render" (appear, or enable when you tick, "create cam") just create the cam
    - opt for later : "use cam name" if already in cam, output the name of the cam ? (with suffixes...)
- User preferences for defaults values (default placeholder, date format, auto-padding, name normalization)

2020-02-11 (1, 0, 3):  
- fix open folder bug
- removed openGl render though cam button, appears in solid mode only with aview_context False :  
render.opengl(animation=False, sequencer=False, write_still=True, view_context=False)