# Quick_render

Blender addon - Render and save view/cam in one click

**[Download latest](https://github.com/Pullusb/Quick_render/archive/master.zip)**

---

# Description

The goal is simple : Be able to export view snapshots in 3D view and iterate quickly.  
Press a button and it's exported, you didn't name anything ? fine, you can but don't have to.  
  

First use case exemple :  
You have the realisator/client/bossman/whatever behind you that navigate with you in the scene to extract some reference views.  

The guy : This point of view is nice can you export the..  
You : \[click\] Done.  
The guy : huuu ok... \[Look at you navigating...\] Ah! This view is cool too mayb..  
You : \[click\] Done !  
The guy : ...and this slight different angle is...  
You : \[click\] Doooone !!  
The guy : \[suspicious\] What ?! huu ooooookaay... you sure ?  
You : \[click (showing exported file)\] Yep, there.  
The guy : \[whispering to himself\] Wow that was way too fast ! What a pro, I admire him so much, lets make HIM the boss, oh yeah !  
You : \[Getting a big head\] Yup... thats me ! (hint : you shouln't say that last line, it totally breaks the hype... Trust me).  
  
Second use case (solo) :  
You : \[thinking nervously\] I need this render out now !... Quick ! I'll have to press F12 then Alt+S, navigate to saving location (probably aside blend file !) then choose a name and Oh wait!...  
it's done.


### options: 

In the name field you can use padding number like "my-beloved-cube_##"



## Todo:


- "True Render" from view button
    
- Setup user preferences for defaults values

- When user use his own padding '####', behavior is totally different with date/frame infos insertion. Check how to make this consistent

- Add an option to create camera at current view (using view matrix and simple hacks)...

Optional

- View History:
    Store trigerred view history of each render (maybe with a unique ID number + auto name given) as UI list
    This way the user can Go back to a view with history (if realisator/client/bossman thinks this export is cool) and place a cam on this view
    A bit overkill but I like it !