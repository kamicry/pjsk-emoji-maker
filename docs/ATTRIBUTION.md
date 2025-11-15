# Attribution

## Character Images

### Source

The character images used in this plugin are sourced from the [koishi-plugin-pjsk-pptr](https://github.com/kamicry/koishi-plugin-pjsk-pptr) project.

**Repository**: https://github.com/kamicry/koishi-plugin-pjsk-pptr  
**Import Date**: November 15, 2024  
**Total Images**: 115 PNG files

### Image Organization

Images are organized by character in the `pjsk_emoji/assets/img/` directory:

- **Miku** (`img/Miku/`): 18 images
  - Chinese name: 初音未来
  - Group: MORE MORE JUMP!

- **Ichika** (`img/Ichika/`): 18 images
  - Chinese name: 星乃一歌
  - Group: Leo/need

- **Saki** (`img/Saki/`): 18 images
  - Chinese name: 天马咲希
  - Group: Leo/need

- **Honami** (`img/Honami/`): 18 images
  - Chinese name: 望月穗波
  - Group: Leo/need

- **Shiho** (`img/Shiho/`): 18 images
  - Chinese name: 日野森志步
  - Group: Leo/need

- **Akito** (`img/Akito/`): 13 images
  - Chinese name: 东云彰人
  - Group: Vivid BAD SQUAD

- **Touya** (`img/Touya/`): 18 images
  - Chinese name: 青柳冬弥
  - Group: Vivid BAD SQUAD

- **Kohane** (`img/Kohane/`): 15 images
  - Chinese name: 小豆泽心羽
  - Group: Nightcord at 25:00

### Image Naming Convention

Each character directory contains numbered PNG files following the pattern: `<CharacterName>_<number>.png`

Examples:
- `Miku_01.png`
- `Ichika_02.png`
- `Saki_03.png`

### License Information

These images are imported and used in accordance with the original project's license terms. Users and developers are responsible for ensuring compliance with any applicable licensing requirements.

For the original project's license, please refer to:
https://github.com/kamicry/koishi-plugin-pjsk-pptr/blob/main/LICENSE

### Usage

The images are integrated into the plugin's rendering system through the `characters.json` configuration file. Each character entry includes:

- `character_images_path`: Path to the character's image directory
- `image_path`: Path to the default emoji image (used for quick reference)

The renderer can access these images programmatically:

```python
from pjsk_emoji.domain import CHARACTERS
from pjsk_emoji.renderer import PJSKRenderer

renderer = PJSKRenderer()
character_data = renderer._get_character_data("初音未来")
images_path = character_data.get('character_images_path')  # Returns "img/Miku"
```

### Acknowledgments

Special thanks to the [koishi-plugin-pjsk-pptr](https://github.com/kamicry/koishi-plugin-pjsk-pptr) project maintainers for providing these character images and maintaining the original resource.

---

**Last Updated**: November 15, 2024  
**Maintainer**: pjsk-emoji-maker plugin team
