# User Guide Images - Fixed!

## Problem
User Guide images used hardcoded path:
```
C:\Users\minh\.gemini\antigravity\brain\166dbfc7-5412-46ec-abff-6279f0f6eb85\
```

This won't work on other computers!

## Solution
✅ **Bundled images into project**

### Changes Made:
1. **Created folder**: `assets/guide_images/`
2. **Copied images**:
   - guide_project_setup.png
   - guide_fuzzy_ahp_input.png
   - guide_fuzzy_ahp_results.png
   - guide_topsis_rating.png
   - guide_project_info.png

3. **Updated code**: `gui/user_guide_dialog.py`
   ```python
   # OLD - Hardcoded path ❌
   self.artifacts_dir = os.path.join(
       os.path.expanduser("~"),
       ".gemini", "antigravity", "brain", "166dbfc7-..."
   )
   
   # NEW - Relative path ✅
   current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
   self.artifacts_dir = os.path.join(current_dir, "assets", "guide_images")
   ```

## Result
- ✅ Images now bundled with app
- ✅ Works on any computer
- ✅ No dependency on user's .gemini folder

## To Add More Images
Simply copy PNG files to `assets/guide_images/` folder!
