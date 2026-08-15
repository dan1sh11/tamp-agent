from nli.interface import process_instruction

from simulation.actions import Action
from simulation.environment import TAMPEnvironment
from simulation.executor import PlanExecutor

def main():
    #NLI
    '''
    while True:
        try:
            user_input = input("Robot instruction (Press Ctrl + D to terminate): ")

            instruction = process_instruction(user_input)

            print(instruction.model_dump_json(indent=2))
        except EOFError:
            print()
            break
    '''
    #Simulation
    env = TAMPEnvironment(gui=True)

    while True:
        try:
            print("Loaded objects:")
            for name in env.registry.names():
                print(f"  - {name}")

            executor = PlanExecutor(env)
            executor.execute(demo_plan())

            print("Demo complete. Close the PyBullet window to exit.")
            env.run_forever()

        except EOFError:
            env.close()


def demo_plan():
    # Same normalized interface the future Fast Downward adapter will emit.
    return [
        Action.home(),
        #Action.move_to("cube_red"),
        #Action.grasp("cube_red"),
        #Action.home(),
        #Action.release(),
        #Action.home(),
    ]
    



if __name__ == "__main__": main()