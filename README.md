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

**Filename** : If not specified get a placeholder name like 'view_01'.  
Image will never be overwritten, always save while auto incrementing name 
You can use padding number like "my-beloved-cube_###", if not specified, automatic padding is 2 digits 

Exemples with name : beloved-cube

**insert date** : beloved-cube\_2020-02-11

**insert frame**: beloved\_cube\_0250

**Both** : beloved\_cube\_2020-02-11\_0250 (starting to get confusing)

**open export directory** : Well... it open's it.



## Todo:

- "True Render" from a render view button
    
- Setup user preferences for defaults values (default placeholder, date format, auto-padding)

- When user use his own padding '####', behavior is totally different with date/frame infos insertion. Check how to make this consistent

- Add an option to create camera at current view (using view matrix and simple hacks)...

Optional

- View History:
    Store trigerred view history of each render (maybe with a unique ID number + auto name given) as UI list
    This way the user can Go back to a view with history (if realisator/client/bossman thinks this export is cool) and place a cam on this view
    A bit overkill but I like it !