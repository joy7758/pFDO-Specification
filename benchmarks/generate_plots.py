import numpy as np
import matplotlib.pyplot as plt

def generate_rlcp_plots():
    # Simulation Parameters
    iterations = np.arange(1, 101)
    alpha_base = 0.5
    
    # Simulate dynamic alpha increasing over time (representing increased unlearning pressure)
    alpha_values = np.linspace(0.5, 2.0, 100)
    
    # Simulate Loss Components
    # L_survival: Decreases as model adapts (Logarithmic decay)
    l_survival = 5 * np.exp(-0.05 * iterations) + 0.5
    
    # L_unlearning: Initially high, decreases as knowledge is decoupled, 
    # but weighted heavily by increasing alpha
    raw_unlearning = 10 * np.exp(-0.03 * iterations)
    l_unlearning_weighted = alpha_values * raw_unlearning
    
    # L_total calculation
    l_total = l_survival + l_unlearning_weighted
    
    # Plotting
    plt.figure(figsize=(10, 6))
    
    plt.plot(iterations, l_total, label=r'$L_{total}$', color='black', linewidth=2)
    plt.plot(iterations, l_survival, label=r'$L_{survival}$', linestyle='--', color='blue', alpha=0.7)
    plt.plot(iterations, l_unlearning_weighted, label=r'$\alpha \cdot L_{unlearning}$', linestyle='-.', color='red', alpha=0.7)
    
    plt.title(r'RLCP Loss Convergence: Impact of $\alpha$ on Knowledge Decoupling', fontsize=14)
    plt.xlabel('Training Iterations', fontsize=12)
    plt.ylabel('Loss Value', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Add annotation for Memory Wall Logic
    plt.annotate('Memory Wall Decoupling Point', xy=(40, l_total[39]), xytext=(50, 8),
                 arrowprops=dict(facecolor='black', shrink=0.05),
                 fontsize=10)

    # Save as PDF for high-quality LaTeX integration
    output_path = 'FDO_Project/DOIP-Segments-Specification/loss_curve.pdf'
    plt.savefig(output_path, format='pdf', bbox_inches='tight')
    print(f"Plot generated: {output_path}")

if __name__ == "__main__":
    generate_rlcp_plots()
