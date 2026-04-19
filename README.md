# wayconfig

Hyprland desktop config with:

- `waybar` top/bottom bar
- `eww` clickable workspace strip with `[n]` active workspace formatting
- `rofi` app launcher, system menu, and wallpaper picker
- `swaync` notifications/control center
- `bluepala` and `netpala` popup TUIs
- floating terminal power menu

## Structure

- [hypr](./hypr)
- [waybar](./waybar)
- [eww](./eww)
- [rofi](./rofi)
- [swaync](./swaync)
- [tui](./tui)

## Install

Install packages:

```bash
./install-waybar-deps.sh
```

Symlink this repo into `~/.config`:

```bash
./install-config-links.sh
```

Reload Hyprland and restart the bar:

```bash
hyprctl reload
~/.config/launch-bar.sh
```

## Main Behavior

- Workspaces are rendered by `eww`, clickable, and show the active one as `[n]`.
- Waybar hosts the clock, tray, system menu trigger, usage indicators, brightness, volume, Bluetooth, Wi‑Fi, and battery.
- Bluetooth click opens `bluepala` in floating `kitty`.
- Wi‑Fi click opens `netpala` in floating `kitty`.
- Battery click opens the power menu in floating `kitty`.
- The extra right-side menu button opens the `rofi` system menu.

## Keybinds

- `Super+Space`: app launcher (`rofi`, bento/grid style)
- `Super+P`: system menu (`rofi`)
- `Super+N`: swaync control center
- `Super+V`: clipboard menu
- `Super+Shift+S`: region screenshot
- `Print`: fullscreen screenshot

## System Menu

`Super+P` or the top-bar menu button opens:

- Wallpaper
- Hyprland Config
- Reload Hyprland
- Restart Bar
- Record Fullscreen
- Record Region
- Stop Recording
- Recordings Folder
- Audio Mixer
- Bluetooth
- Wi‑Fi
- Power

## Wallpaper Picker

The wallpaper menu reads from:

```text
~/Pictures/Wallpapers
```

Supported file types:

- images: `png`, `jpg`, `jpeg`, `webp`, `bmp`, `gif`
- videos: `mp4`, `webm`, `mkv`, `mov`

It calls your existing `eink-wallpaper` script with the selected file.

## Notes

- AUR installs prefer `paru`, then fall back to `yay`.
- `rofi` menu icons use downloaded Feather SVGs in [rofi/icons/external](./rofi/icons/external).
- `swaync` is styled to match the square-corner grayscale theme.
- If tray apps do not appear, the app itself may need tray support enabled.
