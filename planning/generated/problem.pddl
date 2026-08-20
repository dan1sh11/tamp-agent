(define (problem tamp-task)
    (:domain tamp-agent)
    (:objects
        large_cube_red - object
        large_cube_blue - object
        cylinder_green - object
        cylinder_yellow - object
        sphere - object
        capsule - object
        small_cube_red - object
        cylinder_red - object
        small_cube_blue - object
        box - receptacle
    )
    (:init
        (on-table large_cube_red)
        (on-table large_cube_blue)
        (on-table cylinder_green)
        (on-table cylinder_yellow)
        (on-table sphere)
        (on-table capsule)
        (on-table small_cube_red)
        (on-table cylinder_red)
        (on-table small_cube_blue)
        (hand-empty)
    )
    (:goal
        (holding cylinder_green)
    )
)
