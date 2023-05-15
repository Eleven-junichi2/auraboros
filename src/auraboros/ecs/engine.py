class Component:
    pass


class MovementSystem(System):
    def update(self):
        for entity in self.entities:
            position = entity.get_component("Position")
            velocity = entity.get_component("Velocity")
            if position and velocity:
                position.x += velocity.x
                position.y += velocity.y


# Example usage
player = Entity()
player.add_component(Position(0, 0))
player.add_component(Velocity(1, 1))

enemy = Entity()
enemy.add_component(Position(10, 10))
enemy.add_component(Velocity(-1, -1))

entities = [player, enemy]

movement_system = MovementSystem(entities)

for i in range(10):
    movement_system.update()
    print(player.get_component("Position").x, player.get_component("Position").y)
    print(enemy.get_component("Position").x, enemy.get_component("Position").y)
