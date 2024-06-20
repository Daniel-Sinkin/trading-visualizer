# trading-visualizer
A tool written in OpenGL and PyGame that can read in historic tick data and interactively plot it 

## Notes
### Version 0 instead of Version 330 in OpenGL
The order of the creation of the objects is important, the following works:
```python
def setup_pygame_and_opengl(self):
    pg.init()

    pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
    pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
    pg.display.gl_set_attribute(
        pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE
    )
    pg.display.gl_set_attribute(pg.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)

    self.pg_window: pg.Surface = pg.display.set_mode(
        (1600, 900), flags=pg.OPENGL | pg.DOUBLEBUF
    )

    self.ctx: Context = mgl.create_context()
    self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
```
while the following does not:
```python
def setup_pygame_and_opengl(self):
    pg.init()

    self.pg_window: pg.Surface = pg.display.set_mode(
        (1600, 900), flags=pg.OPENGL | pg.DOUBLEBUF
    )

    pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
    pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
    pg.display.gl_set_attribute(
        pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE
    )
    pg.display.gl_set_attribute(pg.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)


    self.ctx: Context = mgl.create_context()
    self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
```

### No window appears
Check if you're actually getting the event queue every frame, even if you're not doing anything significant with it.
```python
def handle_events(self):
    for event in pg.event.get():
        if event.type == pg.QUIT:
            self.is_running = False
```