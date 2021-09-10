import utils
import viewer
import env
import gui

import time

main_env = env.Env()
main_viewer = viewer.Viewer('EvoGym Design Interface')
#gui_viewer = gui.GUI('EvoGym Design Interface GUI')

def main():
    while not main_viewer.get_window_close():
        main_viewer.render(main_env.grid)
        #gui_viewer.update()
        main_env.update(
            main_viewer.currently_hovered,
            main_viewer.currently_selected,
            main_viewer.mouse_press,
            main_viewer.mouse_held,
            main_viewer.get_key_presses())

        # print(main_viewer.get_key_presses())
        #time.sleep(0.2)
    main_viewer.safe_close()
if __name__ == "__main__":
    main()