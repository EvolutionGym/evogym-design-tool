import utils
import viewer
import env
import gui

import time

main_env = env.Env()
main_viewer = viewer.Viewer('EvoGym Design Interface')
gui_viewer = gui.GUI('EvoGym Design Interface GUI', main_viewer.window_data)

def main():
    while not main_viewer.get_window_close():
        main_viewer.render(
            main_env.grid, main_env.objects,
            main_env.hovered_object_id,
            main_env.selected_object_id,
            main_env.mode)
        gui_viewer.update()
        main_env.update(
            main_viewer.currently_hovered,
            main_viewer.currently_selected,
            main_viewer.mouse_press,
            main_viewer.mouse_held,
            main_viewer.get_key_presses())

        #utils.get_objects(main_env.grid)
        #time.sleep(1)

        # print(main_viewer.get_key_presses())

    main_viewer.safe_close()
if __name__ == "__main__":
    main()