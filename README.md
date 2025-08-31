# Emotional_damage-

Game Description
Mood Bullet Arena is a 3D action-survival arena game where the player must tactically use “mood bullets” or close-range slaps to control and eliminate enemies.
 Each bullet changes an enemy’s mood, affecting their behavior, movement, and the player’s score.
 You start with a limited number of bullets, gain extra bullets when enemies die, and the game ends when you either run out of bullets or get slapped by enemies 5 times.
The longer you survive, the more intense the fight becomes — every time an enemy dies, the movement speed of all remaining enemies increases, making them rush toward you faster.
 The game will inevitably reach a breaking point where survival is nearly impossible.

Main Mechanics
Mood Bullets


Red – Angry → Runs toward nearest enemy to slap them out (+15 points per kill). Duration: 4 sec.


Yellow – Happy → Spins/dances in place for 4 sec (–5 points).


Blue – Crying → Stops moving, drops “tears”. If slapped → +10 points & attacks nearest Happy enemy. Duration: 4 sec.


Purple – Scared → Runs away from player for 4 sec, then dies & spawns a new random enemy (+20 points).


Green – Confused → Wanders randomly for  sec (+1 point/sec survived).


Bullet System


Start with X bullets (random moods).


Every time an enemy dies → gain 1 random bullet.


If bullet count = 0 →  kill enemies to get more bullets


Player Slap System


Press F when close to an enemy to slap them.  LMAO!



Enemy Slap System


Enemies can also slap the player if they get close.


5 enemy slaps = Player dies → Game Over.


Difficulty Scaling


Each time any enemy dies, the speed of all remaining enemies increases.


Makes enemies harder to avoid over time, ensuring the game has a natural end point.


Member 1 – Pratyasha Roy 24241115
What: Move player forward, backward, left, right in the arena.


How: Updates player position while keeping them inside boundaries.


Keys: W = Forward, S = Backward, A = Left, D = Right.


Feature 2 – Camera Control
What: Move camera up/down/left/right and toggle camera mode.


How: Arrow keys move the camera, right mouse click toggles between fixed & follow mode.


Keys: Arrow Keys, Right Mouse Click.


Feature 3 – Bullet Shooting System
What: Fire bullets of different moods that change enemy behavior.


How: Select bullet type with number keys, shoot with left mouse click.


Keys: 1–5 to select bullet mood, Left Mouse Click to shoot.


Feature 4 – Bullet Inventory & Game Over
What: Start with limited bullets, gain +1 random bullet on each enemy death. Not a feature


How: If bullet count reaches 0 → enemy deaths spawns more bullets


Keys: Automatic system, no specific key.



Member 2 – Mohammad Aseer Intisar-24241116



Feature 1 – Mood Change System (5 Moods)
Red – Angry: Runs to nearest enemy & slaps them out (+15 points).


Yellow – Happy: Spins in place for 8 sec (–5 points).


Blue – Crying: Stops & drops “tears”; if slapped → +10 points & attacks Happy enemy.


Purple – Scared: Runs away 12 sec, then dies & spawns new enemy (+20 points).


Green – Confused: Wanders randomly for 12 sec (+1 point/sec survived).


Feature 2 – Mood Cooldown System
What: Mood lasts fixed time (8 or 12 sec) before returning to Neutral.


How: Uses per-enemy timer reset after shot.


Feature 3 – Difficulty Scaling
What: Every time an enemy dies, all remaining enemies move faster.


How: Global enemy speed variable increases on each death.



Member 3 – A K M Foyshal Sarkar -22201686 
Feature 1 – Cheat Mode

What:
Special mode that gives the player unfair advantages such as infinite bullets, restoring lives, or slowing enemies.

How:

Press C to toggle Cheat Mode (ON/OFF).

While Cheat Mode is ON:

I → Infinite bullets for 10 seconds.

H → Restore all 5 lives instantly.

k → Slow down all enemies for 5 seconds.





Why:
Adds a fun and experimental option for players to survive longer, test different situations, and enjoy “god mode” mechanics without breaking the main gameplay balance.



Feature 2 – Enemy Slap System
What: Enemies try to slap the player if close.


How:


Player has 5 lives (slaps taken).


On 5th slap → Player dies, Game Over.


Feature 3 – Enemy Spawning & Neutral Movement
What: Spawn enemies at random locations, move them around arena in neutral state.


How: Random wander random until mood changes.
