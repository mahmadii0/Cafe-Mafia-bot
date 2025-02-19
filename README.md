# Cafe Mafia

This project is a Telegram bot for the Mafia game, based on the Iranian scenario. It is my first project, developed using Python! Below, I'll highlight a few points about the project. If you have any suggestions for improvements, I'd be happy to hear them!

## Key Points
1. The strings in this project are in **English**.  
   (when you use a persian text command, the language of game will change to **Persian**)
   
3. I haven't used `async/await` since it wasn't necessary for this project—and it works perfectly fine! 😂

5. The constants.py file, need to change for database conncetion detail and bot token

---

## Game Scenario
Godfather 3 is a social deduction hidden-role game based on reasoning and inference. In this game, players are divided into three groups: the majority citizens, the mafia team, and a single independent role.

The roles are secret, known only to their owners and the moderator. The goal of the citizens is to take control of the city and eliminate the mafia, while the mafia wins if they equal the number of citizens—except for Jack, who has different conditions.

The game consists of alternating night and day phases.

### Game Roles

#### Godfather
- **Abilities**:  
  - Immune to Leon's one-shot night attack.  
  - Has a vest for protection.  
  - Determines the group's night shot. If eliminated, other members take over the shooting.  
  - Has the ability of the **sixth sense**, which allows unique insights during the night.  

#### Saul Goodman
- **Abilities**:  
  - Can trade and buy instead of shooting at night.  
  - Can turn a simple citizen into a mafia member once.  
  - During the trade, the target is marked, and the moderator facilitates the transition.  

#### Matador
- **Abilities**:  
  - Wakes up with the mafia team at night.  
  - Can remove a player's night ability by targeting them.  
  - If the targeted player wakes up that night, they face consequences decided by the moderator.  

#### Sherlock Holmes
- **Role**: Standalone  
- **Abilities**:  
  - Immortal during the first two nights of the game.  
  - Can play on the mafia, citizen, or independent side.  
  - Wakes up before the mafia and can assume the role of any player.  

#### Dr. Watson
- **Abilities**:  
  - Can save one person’s life each night (citizen or mafia).  
  - Can save himself once during the game.  
  - Unlimited ability to save others.  

#### Leon the Professional
- **Abilities**:  
  - Can shoot a member of the mafia at will.  
  - If he mistakenly shoots a citizen, he dies and cannot be saved by the doctor.  
  - Has a vest that protects him from one shot.  

#### Citizen Kane
(In codes, i wrote Kein)
- **Abilities**:  
  - Can reveal a player's identity on one chosen night.  
  - If he identifies a mafia member correctly, the moderator reveals it to the crowd the next morning.  

#### Constantine
- **Abilities**:  
  - Can revive one expelled player (citizen, mafia, or independent) once per game.  
  - The summoned player retains their role and abilities unless revealed otherwise.  

#### Citizen
- **Role**:  
  - A simple citizen whose goal is to identify mafia members and vote wisely.  
  - Does not have special abilities at night but focuses on teamwork and strategic reasoning for the citizen team’s victory.  


## Night Rules and Conditions
1. **Mafia Abilities**: Each night, the mafia team can choose **one ability**:  
   - Fire a shot.  
   - The Godfather uses their sixth sense.  
     *(If correct, the revealed person is announced in the morning.)*  
   - Saul buys an ordinary citizen.  

   *Note: These abilities cannot all be used in the same night. Other players will not know which ability was chosen.*

2. **Saul’s Purchase**: When Saul attempts to buy Goodman, the moderator announces this action.

3. **Sherlock’s Victory Conditions**:  
   - If Sherlock reaches **K-Ace** and shakes hands, Sherlock wins.  
   - If Sherlock is voted out during the day, Sherlock loses.

4. **Citizen Special Roles**:  
   - If a citizen is **Keenshot**, their inquiry results are not revealed at night.  
   - On the **night of slaughter**, it’s recommended to inquire about the next day’s situation.

5. **Godfather’s Slaughter**: A player slaughtered by the Godfather cannot use their ability that night.

6. **KAS Handshake Outcomes**:  
   - **Citizen shakes hands with the mafia → Mafia wins.**  
   - **Citizen shakes hands with Sherlock → City wins.**  
   - **Sherlock shakes hands with the mafia → Sherlock wins.**

7. **Game Endings**:  
   - If the citizens expel all mafia members and Sherlock remains, the **citizens win**.  
   - If the number of mafia equals the remaining players, the **mafia wins**.

---

