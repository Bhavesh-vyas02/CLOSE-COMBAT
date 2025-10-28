# Complex AI System Documentation

## Overview

This fighting game features an advanced AI system with machine learning capabilities, pattern recognition, and adaptive difficulty. The AI learns from player behavior and adjusts its strategy in real-time.

## AI Features

### 1. **Character-Specific Personalities**

Each character has unique AI traits:

- **Warrior**: Balanced tactical fighter (70% aggression, good counter-skills)
- **Wizard**: Strategic long-range specialist (50% aggression, high intelligence)
- **Huntress**: Aggressive hit-and-run expert (80% aggression, combo-focused)
- **King**: Master fighter with balanced skills (60% aggression, excellent counters)
- **Hero Knight**: Noble defensive fighter (70% aggression, strong defense)
- **Martial Hero**: Extremely aggressive close-combat specialist (90% aggression)

### 2. **Advanced AI States**

The AI operates in different behavioral states:

- **ANALYZING**: Learning player patterns, cautious behavior
- **AGGRESSIVE**: Rush-down tactics, frequent attacks
- **DEFENSIVE**: Survival focus, counter-attacks only
- **COMBO**: Chain attack sequences
- **COUNTER**: Wait for openings, punish mistakes

### 3. **Pattern Recognition System**

- Records last 20 player actions
- Detects attack patterns and movement habits
- Adapts behavior based on discovered patterns
- Increases prediction accuracy over time

### 4. **Machine Learning Features**

- **Adaptation Level**: AI gets better at predicting player behavior
- **Prediction Accuracy**: Tracks successful predictions
- **Memory System**: Remembers effective strategies
- **Dynamic Difficulty**: Adjusts challenge based on player performance

### 5. **Advanced Combat Techniques**

- **Feint System**: AI can fake movements to bait players
- **Zone Control**: AI prefers certain screen areas based on character
- **Combo Chains**: Executes character-specific combo sequences
- **Counter-Attack Windows**: Punishes player mistakes with precise timing
- **Risk Assessment**: Evaluates danger level and adjusts accordingly

### 6. **Stamina Management**

- AI manages virtual stamina for realistic behavior
- Reduces action intensity when "tired"
- Prevents unrealistic constant aggression

### 7. **Dynamic Difficulty Adjustment**

- Monitors AI win/loss ratio
- Automatically adjusts difficulty if AI is too easy/hard
- Modifies reaction time and aggression
- Maintains balanced, fun gameplay

## Technical Implementation

### AI Decision Making Process:

1. **Pattern Analysis**: Study player's recent actions
2. **State Update**: Transition between behavioral states
3. **Risk Assessment**: Evaluate current situation danger
4. **Position Analysis**: Determine optimal positioning
5. **State-Specific Behavior**: Execute actions based on current state
6. **Advanced Techniques**: Apply feints, baits, predictions
7. **Stamina Check**: Manage action intensity

### Key AI Attributes:

- `ai_adaptation_level`: How well AI has learned player (0.0-1.0)
- `ai_prediction_accuracy`: Success rate of predictions (0.0-1.0)
- `ai_risk_assessment`: Current danger level (0.0-1.0)
- `ai_stamina_management`: Virtual stamina (0-100)
- `ai_state_machine`: Current behavioral state
- `ai_player_pattern_history`: Recent player actions

## Debug Information

Enable AI debug display in main.py by uncommenting:

```python
draw_ai_debug_info(fighter_2, 20, 100)
```

This shows:

- Current AI state
- Adaptation level
- Prediction accuracy
- Risk assessment
- Stamina level
- Combo counter
- Pattern history size

## Difficulty Levels

The AI automatically adjusts between difficulty levels:

- **Easy**: Slower reactions, less aggressive
- **Normal**: Balanced behavior (default)
- **Hard**: Faster reactions, more aggressive
- **Adaptive**: Continuously adjusts based on player performance

## Character-Specific AI Behaviors

### Warrior AI:

- Balanced approach/retreat tactics
- Good at reading player patterns
- Uses both attack types effectively
- Moderate combo usage

### Wizard AI:

- Maintains long range
- Highly strategic
- Excellent at countering
- Patient, waits for openings

### Huntress AI:

- Aggressive rushing
- Heavy combo focus
- Hit-and-run tactics
- Low patience, high aggression

### King AI:

- Master of all techniques
- Excellent counter-attacks
- Balanced positioning
- High adaptation speed

### Hero Knight AI:

- Strong defensive play
- Counter-attack specialist
- Noble, measured approach
- Good stamina management

### Martial Hero AI:

- Extremely aggressive
- Close-combat specialist
- High combo frequency
- Low patience, rushes in

## Performance Optimization

- AI decisions are cached for smooth performance
- Pattern analysis is limited to prevent lag
- State transitions are optimized
- Memory usage is controlled with history limits

This AI system provides a challenging, adaptive opponent that learns and grows with the player, ensuring engaging gameplay that scales with player skill level.
