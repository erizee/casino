dice_rules = """
                pass: 
                    during first round: win on 7 or 11 , lose on 2,3 or 12
                    when none of above are outcomes of throws, the number on dices is now a "Point"
                    during second round: win when "Point" is thrown before 7, lose otherwise
                dpass:
                    during first round: win on 2 or 3, draw on 12, lose on 7 or 11
                    when none of above are outcomes of throws, the number on dices is now a "Point"
                    during second round: win when 7 is is thrown before "Point" , lose otherwise
                Shooter (player currently rolling dices can only bet pass)
                """

dice_commands = """Available commands:
    -Betting:
        [pass|dpass] <amount>
    -Rolling
        roll
    -Game rules
        gmrules
    -Quit
        back"""