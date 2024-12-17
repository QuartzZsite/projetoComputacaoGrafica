import pygame
import math

# Definições de estrutura
class Vertex:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

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
        self.C = Vertex(0, 0, 0)  # Ponto C
        self.N = Vertex(0, 1, -1)  # Vetor N
        self.V = Vertex(0, -1, -1)  # Vetor V
        self.d = 5                  # Distância de projeção
        self.hx = 2                 # Escala horizontal
        self.hy = 2                 # Escala vertical
    
    def load(self, filename):
        with open(filename, 'r') as f:
            line = f.readline().split('=')[1].strip().split()
            self.N = Vertex(float(line[0]), float(line[1]), float(line[2]))
            line = f.readline().split('=')[1].strip().split()
            self.V = Vertex(float(line[0]), float(line[1]), float(line[2]))
            self.d = float(f.readline().split('=')[1].strip())
            self.hx = float(f.readline().split('=')[1].strip())
            self.hy = float(f.readline().split('=')[1].strip())
            line = f.readline().split('=')[1].strip().split()
            self.C = Vertex(float(line[0]), float(line[1]), float(line[2]))

# Funções auxiliares
def world_to_view(v, cam):
    return Vertex(v.x - cam.C.x, v.y - cam.C.y, v.z - cam.C.z)

def project_to_screen(v, cam, width, height):
    x = (v.x * cam.d / v.z) * (width / (2 * cam.hx)) + width / 2
    y = (v.y * cam.d / v.z) * (height / (2 * cam.hy)) + height / 2
    y = height - y # Inverter figura
    return Vertex(x, y, v.z)

def rasterize_triangle(surface, p1, p2, p3):
    # Desenho simples das bordas do triângulo
    pygame.draw.line(surface, (255, 255, 255), (p1.x, p1.y), (p2.x, p2.y))
    pygame.draw.line(surface, (255, 255, 255), (p2.x, p2.y), (p3.x, p3.y))
    pygame.draw.line(surface, (255, 255, 255), (p3.x, p3.y), (p1.x, p1.y))

# Função principal
def main():
    # Inicializa o Pygame
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Computação Gráfica')

    # Carregar malha e parâmetros da câmera
    mesh = Mesh()
    mesh.load('maca2.byu')
    cam = Camera()
    cam.load('camera.txt')

    # Loop principal
    running = True
    while running:
        screen.fill((0, 0, 0))  # Limpa a tela com cor preta
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # Recarregar parâmetros da câmera ao pressionar 'r'
                cam.load('camera.txt')
                print("Parâmetros da câmera recarregados.")
        
        # Desenhar os triângulos
        for triangle in mesh.triangles:
            v1 = project_to_screen(world_to_view(mesh.vertices[triangle.v1], cam), cam, width, height)
            v2 = project_to_screen(world_to_view(mesh.vertices[triangle.v2], cam), cam, width, height)
            v3 = project_to_screen(world_to_view(mesh.vertices[triangle.v3], cam), cam, width, height)
            rasterize_triangle(screen, v1, v2, v3)
        
        pygame.display.flip()  # Atualiza a tela
        pygame.time.delay(16)  # ~60 FPS

    pygame.quit()

# Executa o programa
if __name__ == '__main__':
    main()
