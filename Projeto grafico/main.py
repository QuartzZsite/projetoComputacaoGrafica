import pygame
import numpy as np

class Vertex:
    def __init__(self, x, y, z, nx=0, ny=0, nz=0):
        self.x = x
        self.y = y
        self.z = z
        self.nx = nx
        self.ny = ny
        self.nz = nz

class Triangle:
    def __init__(self, v1, v2, v3):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3

class Mesh:
    def __init__(self):
        self.vertices = []
        self.triangles = []
    
    def load(self, filename):
        with open(filename, 'r') as f:
            num_vertices, num_triangles = map(int, f.readline().split())
            for _ in range(num_vertices):
                x, y, z = map(float, f.readline().split())
                self.vertices.append(Vertex(x, y, z))
            for _ in range(num_triangles):
                v1, v2, v3 = map(int, f.readline().split())
                self.triangles.append(Triangle(v1 - 1, v2 - 1, v3 - 1))

class Camera:
    def __init__(self):
        self.C = np.array([0, 0, 250])
        self.N = np.array([0, 1, -1])
        self.V = np.array([0, 0, -1])
        self.d = 100
        self.hx = 2
        self.hy = 2

    def get_view_matrix(self):
        Z = self.V / np.linalg.norm(self.V)
        X = np.cross(self.N, Z)
        X = X / np.linalg.norm(X)
        Y = np.cross(Z, X)
        Y = Y / np.linalg.norm(Y)

        view_matrix = np.array([
            [X[0], Y[0], Z[0], -np.dot(X, self.C)],
            [X[1], Y[1], Z[1], -np.dot(Y, self.C)],
            [X[2], Y[2], Z[2], -np.dot(Z, self.C)],
            [0, 0, 0, 1]
        ])
        return view_matrix

class Lighting:
    def __init__(self):
        self.Iamb = np.array([100, 100, 100])
        self.Ka = 0.2
        self.Il = np.array([127, 213, 254])
        self.Pl = np.array([60, 5, -10])
        self.Kd = np.array([0.5, 0.3, 0.2])
        self.Od = np.array([0.7, 0.5, 0.8])
        self.Ks = 0.5
        self.eta = 1
    
    def load(self, filename):
        with open(filename, 'r') as f:
            self.Iamb = np.array(list(map(float, f.readline().split('=')[1].split())))
            self.Ka = float(f.readline().split('=')[1])
            self.Il = np.array(list(map(float, f.readline().split('=')[1].split())))
            self.Pl = np.array(list(map(float, f.readline().split('=')[1].split())))
            self.Kd = np.array(list(map(float, f.readline().split('=')[1].split())))
            self.Od = np.array(list(map(float, f.readline().split('=')[1].split())))
            self.Ks = float(f.readline().split('=')[1])
            self.eta = float(f.readline().split('=')[1])

def phong_illumination(normal, view_dir, light_dir, lighting):
    ambient = lighting.Ka * lighting.Iamb
    
    diff = lighting.Kd * lighting.Il * max(0, np.dot(normal, light_dir))
    
    reflect_dir = 2 * normal * np.dot(normal, light_dir) - light_dir
    spec = lighting.Ks * lighting.Il * (max(0, np.dot(reflect_dir, view_dir)) ** lighting.eta)
    
    return np.clip(ambient + diff + spec, 0, 255)

def rasterize_triangle(surface, p1, p2, p3, color):
    pygame.draw.polygon(surface, color, [(p1[0], p1[1]), (p2[0], p2[1]), (p3[0], p3[1])])

def project_vertex(vertex, camera, width, height):
    view_matrix = camera.get_view_matrix()
    vertex_homog = np.array([vertex[0], vertex[1], vertex[2], 1])

    vertex_transformed = np.dot(view_matrix, vertex_homog)

    z = vertex_transformed[2] + camera.d
    x = (vertex_transformed[0] * camera.d) / z
    y = (vertex_transformed[1] * camera.d) / z

    return np.array([x * camera.hx + width // 2, y * camera.hy + height // 2])


def main():
    pygame.init()
    width, height = 1000, 900
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Renderizador Phong')

    mesh = Mesh()
    mesh.load('calice2.byu')
    cam = Camera()
    lighting = Lighting()
    lighting.load('iluminacao.txt')

    view_matrix = cam.get_view_matrix()

    view_dir = -cam.C / np.linalg.norm(cam.C)

    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                lighting.load('iluminacao.txt')
                print("Parâmetros de iluminação recarregados.")

        for triangle in mesh.triangles:
            v1 = np.array([mesh.vertices[triangle.v1].x, mesh.vertices[triangle.v1].y, mesh.vertices[triangle.v1].z])
            v2 = np.array([mesh.vertices[triangle.v2].x, mesh.vertices[triangle.v2].y, mesh.vertices[triangle.v2].z])
            v3 = np.array([mesh.vertices[triangle.v3].x, mesh.vertices[triangle.v3].y, mesh.vertices[triangle.v3].z])
            
            v1_proj = project_vertex(v1, cam, width, height)
            v2_proj = project_vertex(v2, cam, width, height)
            v3_proj = project_vertex(v3, cam, width, height)
            
            normal = np.cross(v2 - v1, v3 - v1)
            normal = normal / np.linalg.norm(normal)
            
            light_dir = (lighting.Pl - v1) / np.linalg.norm(lighting.Pl - v1)
            
            color = phong_illumination(normal, view_dir, light_dir, lighting)
            
            rasterize_triangle(screen, v1_proj, v2_proj, v3_proj, color.astype(int))
        
        pygame.display.flip()
        pygame.time.delay(16)

    pygame.quit()

if __name__ == '__main__':
    main()
