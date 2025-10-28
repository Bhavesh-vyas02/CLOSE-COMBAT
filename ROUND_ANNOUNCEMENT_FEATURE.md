# Round Announcement Feature Implementation

## Overview
Added a round announcement system that displays "ROUND X" in large text at the start of each round, with a fade-out effect before the game begins.

## Implementation Details

### New Variables Added
- `show_round_announcement`: Boolean flag to control when to show the announcement
- `round_announcement_start_time`: Timestamp when the announcement started
- `round_announcement_duration`: Total duration of the announcement (2000ms = 2 seconds)
- `round_announcement_fade_duration`: Duration of the fade-out effect (500ms = 0.5 seconds)

### New Function: `draw_round_announcement()`
- **Purpose**: Renders the round announcement with fade effect
- **Parameters**: 
  - `round_num`: Current round number to display
  - `start_time`: When the announcement started
  - `duration`: Total display duration
  - `fade_duration`: Fade-out duration
- **Features**:
  - Large "ROUND X" text (120pt font) centered on screen
  - Fade-out effect in the last 0.5 seconds
  - Semi-transparent dark background overlay
  - Returns `True` while animating, `False` when finished

### Integration Points

#### Game Loop Integration
- Round announcement is checked and drawn before the intro countdown
- Only shows when `show_round_announcement` is `True`
- Prevents intro countdown from starting until announcement finishes

#### Round Reset Integration
- Announcement is reset when starting a new round after round victory
- Announcement is reset when restarting the match from victory menu
- Ensures every round starts with the appropriate announcement

## Visual Design
- **Text**: "ROUND 1", "ROUND 2", "ROUND 3" in large white text
- **Font**: Turok font at 120pt size for maximum visibility
- **Background**: Semi-transparent black overlay (alpha = 85)
- **Animation**: 1.5 seconds solid display + 0.5 seconds fade-out
- **Position**: Centered on screen

## User Experience
1. When a round starts, "ROUND X" appears immediately
2. Text displays for 1.5 seconds at full opacity
3. Text fades out over 0.5 seconds
4. Normal intro countdown begins (5, 4, 3, 2, 1)
5. Game starts normally

## Technical Notes
- Uses per-pixel alpha blending for smooth fade effect
- Integrates seamlessly with existing pause and timer systems
- Does not interfere with existing game state management
- Automatically handles all three rounds (1, 2, 3)