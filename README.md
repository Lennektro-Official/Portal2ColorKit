<h1 align='left'>
  <img width="100" align="left" alt="rainbow_portal" src="https://github.com/user-attachments/assets/a490add4-3d95-43a7-8d16-24bc9cc06977" />
  <br>Portal 2<br>&nbsp;Color Kit
</h1>

<br>

# What is this?
Since it is notoriously annoying and hard to properly change especially the singleplayer portal colors in Portal 2, I wrote a python script that allows you to just specifiy the colors your heart desires in an options file and then
handles dynamically generating the required textures, packing them into a vpk and patching the hardcoded color values in the client. So that means that this will also properly recolor your crosshair and particles in singleplayer without
breaking the crosshair in coop or for mono portal guns. Although it is unlikely, a future game update might break the patches required to patch the client, in that case I will probably publish an update with the new patches.

# How to install and setup
1. Make sure you have Python 3.10 or newer installed on your system
2. Download the latest [release](https://github.com/Lennektro-Official/Portal2ColorKit/releases)
3. Put the *color_kit* folder into your *Portal 2* folder (not *portal2*!)
4. Create a new dlc folder and make sure you have no other vpks in that folder
5. Open the *options.ini* and change the **DlcFolder** property to the number of the dlc folder you want to use for the color kit

# Hot to use
Now you can just change the color values in the *options.ini* to your heart's content. Then you just have to run the *apply* file on Linux or the *apply.bat* on Windows respectively, while making sure your game is closed.
> NOTE: You have to reapply every time you change your settings or the game updates

<br>

## A little disclaimer
This probaly shouldn't happen, but a future game update could break the patches, then you'll have to wait until I get around to fixing that. It also could in theory break your game and make it not boot if they break something in
an update. But don't worry, then you can just go to the *color_kit/bin* folder where the patcher backups the libraries to, and you should find the *client.so* and *client.dll* respectively, depending on what game versions you have
installed on your system and can replace the *client.so* and *client.dll* in your *portal2/bin* folder with those and then just delete all vpk files in the dlc folder you chose for the color kit. Btw. this is also how you uninstall
the color kit.
