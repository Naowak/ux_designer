from PIL import Image, ImageDraw, ImageFont, ImageFilter
from kivy.app import App
from kivy.graphics import Rectangle, Color
from kivy.uix.image import Image as ImageDisplay
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout

def rounded_rect(size, radius, color) :
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    size_x, size_y = size

    # Corner up left
    draw.pieslice(xy=[(0, 0), (2*radius, 2*radius)],
                  start=180,
                  end=270,
                  fill=color)
    # Corner up right
    draw.pieslice(xy=[(size_x-2*radius, 0), (size_x, 2*radius)],
                  start=270,
                  end=360,
                  fill=color)
    # Corner down left
    draw.pieslice(xy=[(0, size_y-2*radius), (2*radius, size_y)],
                  start=90,
                  end=180,
                  fill=color)
    # Corner down right
    draw.pieslice(xy=[(size_x-2*radius, size_y-2*radius), (size_x, size_y)],
                  start=0,
                  end=90,
                  fill=color)

    # Fill inside
    draw.rectangle(xy=[(0, radius), (radius, size_y-radius)],
                   fill=color)
    draw.rectangle(xy=[(radius, 0), (size_x-radius, size_y)],
                   fill=color)
    draw.rectangle(xy=[(size_x-radius, radius), (size_x, size_y-radius)],
                   fill=color)

    return img


def ux_area(color, path, size=(300, 300), corner_radius=120, dist=15, diff_light=10, diff_dark=20, gaussian_radius=10) :

    def fit_bg(img, bg, anchor, color) :
        color = tuple(list(color[:3]) + [0])
        new = Image.new('RGBA', bg.size, color)
        new.paste(img, anchor, img)
        return new

    def paste_image(img, bg, color) :
        # # Paste an image at the position anchor
        color = tuple(list(color[:3]) + [0])

        add_img = Image.new('RGBA', bg.size, (255, 255, 255, 0))
        add_img.paste(img, (0, 0), img)

        final = Image.new('RGBA', bg.size, (255, 255, 255, 0))
        final = Image.alpha_composite(final, bg)
        final = Image.alpha_composite(final, img)

        return final

    # compute colors
    color_light = tuple([c + diff_light for c in color[:3]] + [255])
    color_dark = tuple([c - diff_dark for c in color[:3]] + [255])

    # create imgs to paste
    size_rounded_rect = tuple(s - 4*dist for s in size)

    img_mid = rounded_rect(size_rounded_rect, corner_radius, color)
    img_light = rounded_rect(size_rounded_rect, corner_radius, color_light)
    img_dark = rounded_rect(size_rounded_rect, corner_radius, color_dark)

    # compute pos
    pos_light = (dist, dist)
    pos_mid = (dist*2, dist*2)
    pos_dark = (dist*3, dist*3)

    # create background
    background = Image.new('RGBA', size, color)

    # fit imgs to background
    img_light = fit_bg(img_light, background, pos_light, color_light)
    img_dark = fit_bg(img_dark, background, pos_dark, color_dark)
    img_mid = fit_bg(img_mid, background, pos_mid, color)

    # apply gaussian filter
    img_light = img_light.filter(ImageFilter.GaussianBlur(radius=gaussian_radius))
    img_dark = img_dark.filter(ImageFilter.GaussianBlur(radius=gaussian_radius))

    # paste rounded rectangle
    background = paste_image(img_light, background, color_light)
    background = paste_image(img_dark, background, color_dark)
    background = paste_image(img_mid, background, color)
    # background.show()

    background.save(path)

    return background


class MyViewApp(App) :

    path_current_img = './tmp/current_img.png'
    default_color = (180, 60, 60, 255)

    def build(self) :

        def update_rect(instance, value) :
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size

        def init_display(self, color) :
            ux_area(color, self.path_current_img)
            with self.display_layout.canvas.before :
                Color(rgba=(color[0]/255, color[1]/255, color[2]/255, color[3]/255))
                self.display_layout.rect = Rectangle(size=self.display_layout.size,
                                                     pos=self.display_layout.size)

        # display : left side of window
        self.display_layout = BoxLayout()
        init_display(self, self.default_color)
        self.display_layout.bind(pos=update_rect, size=update_rect)

        self.image_display = ImageDisplay(source=self.path_current_img)
        self.display_layout.add_widget(self.image_display)
        
        # config : right side of window
        # size
        self.label_size_horizontal = Label(text='Size horizontal')
        self.textinput_size_horizontal = TextInput(text='600', multiline=False)

        self.label_size_vertical = Label(text='Size vertical')
        self.textinput_size_vertical = TextInput(text='300', multiline=False)

        # color
        self.label_color_red = Label(text="Red")
        self.slider_color_red = Slider(min=0, max=255, value=65)
        self.slider_color_red.bind(value=self.on_red_change)

        self.label_color_green = Label(text="Green")
        self.slider_color_green = Slider(min=0, max=255, value=65)

        self.label_color_blue = Label(text="Blue")
        self.slider_color_blue = Slider(min=0, max=255, value=65)

        # diff color
        self.label_color_diff_light = Label(text="Difference with light color")
        self.slider_color_diff_light = Slider(min=0, max=255, value=65)

        self.label_color_diff_dark = Label(text="Difference with dark color")
        self.slider_color_diff_dark = Slider(min=0, max=255, value=65)

        # dist
        self.label_distance = Label(text="Distance")
        self.slider_distance = Slider(min=0, max=50, value=15)

        # radius
        self.label_corner_radius = Label(text="Corner radius")
        self.slider_corner_radius = Slider(min=0, max=300, value=30)

        self.label_gaussian_radius = Label(text="Gaussian radius")
        self.slider_gaussian_radius = Slider(min=0, max=30, value=10)

        self.config_layout = BoxLayout(orientation='vertical')
        self.config_layout.add_widget(self.label_size_horizontal)
        self.config_layout.add_widget(self.textinput_size_horizontal)
        self.config_layout.add_widget(self.label_size_vertical)
        self.config_layout.add_widget(self.textinput_size_vertical)
        self.config_layout.add_widget(self.label_color_red)
        self.config_layout.add_widget(self.slider_color_red)
        self.config_layout.add_widget(self.label_color_green)
        self.config_layout.add_widget(self.slider_color_green)
        self.config_layout.add_widget(self.label_color_blue)
        self.config_layout.add_widget(self.slider_color_blue)
        self.config_layout.add_widget(self.label_color_diff_light)
        self.config_layout.add_widget(self.slider_color_diff_light)
        self.config_layout.add_widget(self.label_color_diff_dark)
        self.config_layout.add_widget(self.slider_color_diff_dark)
        self.config_layout.add_widget(self.label_distance)
        self.config_layout.add_widget(self.slider_distance)
        self.config_layout.add_widget(self.label_corner_radius)
        self.config_layout.add_widget(self.slider_corner_radius)
        self.config_layout.add_widget(self.label_gaussian_radius)
        self.config_layout.add_widget(self.slider_gaussian_radius)

        # main layout
        self.main_layout = GridLayout(cols=2)
        self.main_layout.add_widget(self.display_layout)
        self.main_layout.add_widget(self.config_layout)

        return self.main_layout

    def update_display(self, color) :
        ux_area(color, self.path_current_img)

        self.display_layout.canvas.after.clear()
        with self.display_layout.canvas.before :
            Color(color[0]/255, color[1]/255, color[2]/255, color[3]/255)
            Rectangle(pos=self.display_layout.pos, size=self.display_layout.size)      

        self.image_display.reload()

    def on_red_change(self, instance, value) :
        color = (int(value), 60, 60, 255)
        self.update_display(color)

    


if __name__ == '__main__' :
    MyViewApp().run()