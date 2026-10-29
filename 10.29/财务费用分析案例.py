import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 个性化参数：由学号后两位计算c
LAST2 = 24
c = 1.0 + LAST2 / 100.0

def phi(alpha):
    return alpha**4 - alpha**2 - c*alpha + 5.0

def dphi(alpha):
    return 4.0*alpha**3 - 2.0*alpha - c

# 进退法（原版，带非负截断）
def advance_retreat(phi, alpha0, gamma0, t=2.0, max_iter=100):
    alpha_i, gamma_i = float(alpha0), float(gamma0)
    i, f_i, nfev = 0, phi(alpha_i), 1
    history = [(i, alpha_i, gamma_i, f_i, 'init')]
    alpha = None
    for _ in range(max_iter):
        alpha_next = alpha_i + gamma_i
        if alpha_next <= 0.0:
            alpha_next = 0.0
            f_next = phi(alpha_next); nfev += 1
            if i == 0:
                gamma_i = -gamma_i; alpha = alpha_next
                history.append((i+1, alpha_next, gamma_i, f_next, 'reverse'))
                continue
            else:
                a, b = min(alpha, alpha_next), max(alpha, alpha_next)
                history.append((i+1, alpha_next, gamma_i, f_next, 'stop'))
                return a, b, history, nfev
        f_next = phi(alpha_next); nfev += 1
        if f_next >= f_i:
            if i == 0:
                gamma_i = -gamma_i; alpha = alpha_next
                history.append((i+1, alpha_next, gamma_i, f_next, 'reverse'))
                continue
            else:
                a, b = min(alpha, alpha_next), max(alpha, alpha_next)
                history.append((i+1, alpha_next, gamma_i, f_next, 'stop'))
                return a, b, history, nfev
        else:
            gamma_next = t * gamma_i
            alpha, alpha_i, f_i = alpha_i, alpha_next, f_next
            i += 1; gamma_i = gamma_next
            history.append((i, alpha_i, gamma_i, f_i, 'accept'))
    a, b = min(alpha, alpha_i), max(alpha, alpha_i)
    return a, b, history, nfev

# 修改版进退法：允许负 alpha
def advance_retreat_allow_negative(phi, alpha0, gamma0, t=2.0, max_iter=100):
    alpha_i, gamma_i = float(alpha0), float(gamma0)
    i, f_i, nfev = 0, phi(alpha_i), 1
    history = [(i, alpha_i, gamma_i, f_i, 'init')]
    alpha = None
    for _ in range(max_iter):
        alpha_next = alpha_i + gamma_i
        f_next = phi(alpha_next); nfev += 1
        if f_next >= f_i:
            if i == 0:
                gamma_i = -gamma_i; alpha = alpha_next
                history.append((i+1, alpha_next, gamma_i, f_next, 'reverse'))
                continue
            else:
                a, b = min(alpha, alpha_next), max(alpha, alpha_next)
                history.append((i+1, alpha_next, gamma_i, f_next, 'stop'))
                return a, b, history, nfev
        else:
            gamma_next = t * gamma_i
            alpha, alpha_i, f_i = alpha_i, alpha_next, f_next
            i += 1; gamma_i = gamma_next
            history.append((i, alpha_i, gamma_i, f_i, 'accept'))
    a, b = min(alpha, alpha_i), max(alpha, alpha_i)
    return a, b, history, nfev

# 0.618 法
def golden_section(phi, a0, b0, eps=1e-6, exact=True, max_iter=10000):
    a, b = float(a0), float(b0)
    Ls, history, nfev = [b - a], [], 0
    if exact:
        rho = (np.sqrt(5.0) - 1.0) / 2.0
        sigma = 1.0 - rho
    else:
        sigma, rho = 0.382, 0.618
    p = a + sigma * (b - a)
    q = a + rho * (b - a)
    fp, fq = phi(p), phi(q); nfev += 2
    K = 0
    while True:
        if b - a < eps:
            alpha_star = (a + b) / 2.0
            break
        if K >= max_iter:
            alpha_star = (a + b) / 2.0
            break
        history.append((K, a, b, p, q, fp, fq))
        if fp <= fq:
            a_new, b_new = a, q
            q_new, fq_new = p, fp
            p_new = a_new + sigma * (b_new - a_new)
            fp_new = phi(p_new); nfev += 1
            a, b, p, q, fp, fq = a_new, b_new, p_new, q_new, fp_new, fq_new
        else:
            a_new, b_new = p, b
            p_new, fp_new = q, fq
            q_new = a_new + rho * (b_new - a_new)
            fq_new = phi(q_new); nfev += 1
            a, b, p, q, fp, fq = a_new, b_new, p_new, q_new, fp_new, fq_new
        K += 1
        Ls.append(b - a)
    return alpha_star, K, nfev, Ls, history


if __name__ == "__main__":
    print("="*70)
    print(f"n = {LAST2}, c = {c:.6f}")
    print("="*70)

    # 题目1
    print("\n题目1.1 进退法")
    a, b, hist, nfev = advance_retreat(phi, 0.0, 0.1, t=2.0, max_iter=100)
    print(f"最终区间: [{a:.10f}, {b:.10f}], nfev = {nfev}")
    for row in hist:
        print(row)
    mid = (a + b) / 2.0
    print(f"phi(a)={phi(a):.10f}, phi(mid)={phi(mid):.10f}, phi(b)={phi(b):.10f}")

    print("\n题目1.2 单调递减函数")
    phi_dec = lambda x: np.exp(-x)
    a2, b2, hist2, nfev2 = advance_retreat(phi_dec, 0.0, 0.1, t=2.0, max_iter=100)
    print(f"区间: [{a2:.6f}, {b2:.6f}]")
    for row in hist2[-6:]:
        print(row)

    # 题目2
    print("\n题目2 0.618法（0.382/0.618版）")
    alphaA, KA, NA, LsA, histA = golden_section(phi, a, b, eps=1e-6, exact=False)
    print(f"alpha*={alphaA:.10f}, K={KA}, N={NA}")
    k_arr = np.arange(len(LsA))
    logL = np.log10(np.array(LsA))
    coef = np.polyfit(k_arr, logL, 1)
    print(f"log10 Lk 拟合: slope={coef[0]:.6f}, intercept={coef[1]:.6f}")
    print(f"理论 slope={np.log10(0.618):.6f}")

    # 图2.1
    plt.figure(figsize=(8, 5))
    x_grid = np.linspace(a - 0.2, b + 0.2, 500)
    plt.plot(x_grid, phi(x_grid), label=r'$\phi(\alpha)$')
    plt.axvspan(a, b, color='lightgray', alpha=0.4, label='最终区间')
    for row in hist:
        ii, alpha_i, gamma_i, f_i, action = row
        if action == 'accept':
            plt.plot(alpha_i, f_i, 'o', color='blue')
        elif action == 'stop':
            plt.plot(alpha_i, f_i, 's', color='red')
        elif action == 'init':
            plt.plot(alpha_i, f_i, 'o', color='green')
        elif action == 'reverse':
            plt.plot(alpha_i, f_i, '^', color='orange')
    roots_phi = np.roots([4, 0, -2, -c])
    alpha_ref = roots_phi[np.isreal(roots_phi)].real
    alpha_ref = alpha_ref[alpha_ref > 0][0]
    plt.axvline(alpha_ref, color='k', linestyle='--', label=r'$\alpha^*$')
    plt.xlabel(r'$\alpha$'); plt.ylabel(r'$\phi(\alpha)$')
    plt.title(r'进退法试探点与最终区间，$c=1.24$')
    plt.legend(); plt.grid(True, alpha=0.3)
    plt.tight_layout(); plt.savefig('fig_t1.png', dpi=300)

    # 图2.2
    plt.figure(figsize=(8, 5))
    plt.scatter(k_arr, logL, label=r'$\log_{10}L_k$')
    plt.plot(k_arr, np.polyval(coef, k_arr), 'r-', label='最小二乘拟合')
    plt.xlabel('k'); plt.ylabel(r'$\log_{10}L_k$')
    plt.title('0.618法区间长度收缩')
    plt.legend(); plt.grid(True, alpha=0.3)
    plt.tight_layout(); plt.savefig('fig_t2_length.png', dpi=300)

    # 图2.3
    errs = [abs((row[1] + row[2]) / 2.0 - alpha_ref) for row in histA]
    plt.figure(figsize=(8, 5))
    plt.semilogy(np.arange(len(errs)), np.array(errs) + 1e-300, 'o-')
    plt.xlabel('k'); plt.ylabel(r'$|\alpha_k-\alpha_{\rm ref}|$')
    plt.title('0.618法误差半对数图')
    plt.grid(True, alpha=0.3)
    plt.tight_layout(); plt.savefig('fig_t3_error.png', dpi=300)

    # 题目3 
    print("\n题目3.1 前6次收缩")
    for row in histA[:6]:
        print(row)

    print("\n题目3.3 scipy对比")
    results = []
    res_default = minimize_scalar(phi, bounds=(a, b))
    results.append(('default', res_default.x, res_default.fun,
                    res_default.nfev, getattr(res_default, 'nit', None), res_default.success))
    from scipy.optimize import minimize_scalar

    for method in ['bounded', 'golden', 'brent']:
        if method == 'bounded':
           res = minimize_scalar(phi, bounds=(a, b), method=method)
        else:
           res = minimize_scalar(phi, bracket=(a, b), method=method)
    results.append((method, res.x, res.fun, res.nfev, getattr(res, 'nit', None), res.success))
    
    for item in results:
        print(item)

    print(f"\nalpha_ref = {alpha_ref:.10f}")
    print(f"0.618 A error = {abs(alphaA - alpha_ref):.6e}")
    for item in results:
        print(f"{item[0]}: error={abs(item[1]-alpha_ref):.6e}, nfev={item[3]}")

    # 题目4 
    print("\n题目4 A/B版本精度对比")
    for eps in [1e-6, 1e-8, 1e-10, 1e-12, 1e-14]:
        aA, KAA, NAA, LAA, _ = golden_section(phi, a, b, eps=eps, exact=False)
        aB, KBB, NBB, LBB, _ = golden_section(phi, a, b, eps=eps, exact=True)
        print(f"eps={eps:.0e}: A(K={KAA},L={LAA[-1]:.6e},err={abs(aA-alpha_ref):.6e}), "
              f"B(K={KBB},L={LBB[-1]:.6e},err={abs(aB-alpha_ref):.6e})")

    # 图4.3
    eps_plot = np.logspace(-6, -14, 9)
    errA_plot, errB_plot = [], []
    for eps in eps_plot:
        aA, _, _, _, _ = golden_section(phi, a, b, eps=eps, exact=False)
        aB, _, _, _, _ = golden_section(phi, a, b, eps=eps, exact=True)
        errA_plot.append(abs(aA - alpha_ref))
        errB_plot.append(abs(aB - alpha_ref))
    plt.figure(figsize=(8, 5))
    plt.loglog(eps_plot, errA_plot, 'o-', label='A版 0.382/0.618')
    plt.loglog(eps_plot, errB_plot, 's-', label='B版 精确黄金比')
    plt.xlabel(r'$\epsilon$'); plt.ylabel(r'$|\alpha^*-\alpha_{\rm ref}|$')
    plt.title('A/B两版0.618法误差—精度曲线')
    plt.legend(); plt.grid(True, which='both', alpha=0.3)
    plt.tight_layout(); plt.savefig('fig_t4_AB.png', dpi=300)

    # 题目5 
    print("\n题目5 非单峰函数")
    def psi(alpha): return alpha**4 - 4.0*alpha**2 + alpha + 10.0
    roots_psi = np.roots([4, 0, -8, 1])
    for r in roots_psi:
        print(f"alpha={r:.10f}, psi={psi(r):.10f}, psi''={12*r**2-8:.6f}")

    print("\n修改版进退法（允许负 alpha）")
    for alpha0 in [0.0, 1.0]:
        a5, b5, hist5, nfev5 = advance_retreat_allow_negative(psi, alpha0, 0.1, t=2.0, max_iter=100)
        print(f"alpha0={alpha0}: interval=[{a5:.6f},{b5:.6f}], nfev={nfev5}")
        for row in hist5:
            print(row)

    a_min1, _, _, _, _ = golden_section(psi, -3.1, -0.7, eps=1e-12, exact=True)
    a_min2, _, _, _, _ = golden_section(psi, 1.1, 1.7, eps=1e-12, exact=True)
    print(f"psi 局部极小1: alpha={a_min1:.10f}, psi={psi(a_min1):.10f}")
    print(f"psi 局部极小2: alpha={a_min2:.10f}, psi={psi(a_min2):.10f}")

    # 图5.1
    x_psi = np.linspace(-3, 3, 800)
    plt.figure(figsize=(8, 5))
    plt.plot(x_psi, psi(x_psi), label=r'$\psi(\alpha)$')
    for r in roots_psi:
        plt.plot(r, psi(r), 'o', label=f'驻点 {r:.3f}')
    plt.xlabel(r'$\alpha$'); plt.ylabel(r'$\psi(\alpha)$')
    plt.title(r'非单峰函数 $\psi(\alpha)=\alpha^4-4\alpha^2+\alpha+10$')
    plt.legend(); plt.grid(True, alpha=0.3)
    plt.tight_layout(); plt.savefig('fig_psi.png', dpi=300)

    print("\n所有图像已保存：fig_t1.png, fig_t2_length.png, fig_t3_error.png, "
          "fig_t4_AB.png, fig_psi.png")