import os.path
import cv2
import argparse
import numpy as np



all_mask = {'Green': [np.array([40, 40, 40]), np.array([70, 255, 255])],
            'Yellow': [np.array([15, 0, 0]), np.array([36, 255, 255])],
            'Blue': [np.array([25, 50, 50]), np.array([32, 255, 255])],
            'Red': [np.array([0, 50, 0]), np.array([20, 255, 255])],
            'Orange': [np.array([10, 100, 20]), np.array([25, 255, 255])],
            #   'Pink': [np.array([140, 100, 20]), np.array([165, 255, 255])],
            #   'Violet': [np.array([0, 90, 90]), np.array([180, 255, 255])],
            #   'Purple': [np.array([129, 255, 255]), np.array([158, 50, 70])],
            }


class ObjectDetection:
    def __init__(self):
        self.image = None
        self.final_img = None
        self.blur_image = None
        self.image_hsv = None

    def img_read(self, filename):
        if not os.path.exists(filename):
            raise Exception(f'Image {filename} not found')
        img = cv2.imread(filename)
        return img

    def mask_1(self, mask_name):
        masks = None
        if isinstance(mask_name, str):
            mask_name = [mask_name]
        for name in mask_name:
            name = name.capitalize()
            if name in all_mask:
                lower_bound = all_mask[name][0]
                upper_bound = all_mask[name][1]
                _mask = cv2.inRange(self.image_hsv, lower_bound, upper_bound)
                print(name)
                if masks is None:
                    masks = _mask
                else:
                    masks = masks | _mask
                # print(f'Adding color {name}')
            else:
                print(f'Color {name} is not present. Skipping it')
        return masks

    def apply(self, *args, **kwargs):
        image_path = kwargs.get('image_path', '')
        mask_name = kwargs.get('mask_color', [])
        erode_iteration = kwargs.get('erode_iteration', 9)
        output_path = kwargs.get('output_image', '')

        self.img = self.img_read(image_path)
        # Blur
        self.blur_image = cv2.GaussianBlur(self.img, (5, 5), cv2.BORDER_DEFAULT)
        # Convert to HSV
        self.image_hsv = cv2.cvtColor(self.blur_image, cv2.COLOR_BGR2HSV)

        # Mask
        mask = self.mask_1(mask_name)

        eros = cv2.erode(mask, (3, 3), iterations=erode_iteration)

        self.final_img = cv2.bitwise_or(self.img, self.img, mask=eros)
        if output_path is not None:
            self.fin_image(output_path=output_path, image=self.final_img)

        if kwargs.get('to_display', True):
            # concat_image = np.concatenate((self.img, self.final_img), axis=1)
            # concat_image = cv2.resize(concat_image, (500, 500))

            cv2.imshow('Original Image', self.img)
            cv2.imshow('Final Image', self.final_img)
            # cv2.imshow('Blurred Image', self.blur_image)
            # cv2.imshow('Erode Image', eros)
            # cv2.imshow('HSV Image', self.image_hsv)
            # cv2.imshow('Mask', mask)
            # cv2.imshow(f"Result Image", self.final_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def fin_image(self, *args, **kwargs):
        output_path = kwargs.get('output_path')
        try:
            image = kwargs.get('image')
            cv2.imwrite(output_path, image)
        except:
            print("Error occurred while saving image on {output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Segmentation of Object (Color Based)')
    parser.add_argument('--input', type=str, required=True)
    parser.add_argument('--display', type=str, default=True)

    parser.add_argument('--output', default=None,type=str)
    msg = 'Color to detect you can also give space separate value for example "yellow green". \nAvailable colors :-'
    for key, vale in all_mask.items():
        msg += f'{key}, '

    parser.add_argument('--color', nargs='+', default=['yellow', 'green', 'red', 'blue'], help=msg)
    parser.add_argument('--erode', type=str, default=9, help='Output Image Path')

    args = parser.parse_args()

    input_args = {'image_path': args.input_image,
                  'output': args.output_image,
                  'display': args.to_display,
                  'mask_color': args.detect_color,
                  'erode': args.erode_iteration}

    object_detect = ObjectDetection()
    object_detect.apply(**input_args)

# Terminal Command
# python3 main.py --input_image image.png --output_image output.png --to_display True --detect_color yellow green red blue

