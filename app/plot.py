import matplotlib.pyplot as plt
import numpy as np
import numpy as np
import base64
from io import BytesIO


# plot 2 sine waves with matplotlib
def myplot(amp1, amp2, freq1, freq2, phase1, phase2) -> bytes:
    duration = 1
    sample_rate = 100
    x = np.linspace(0, duration, int(sample_rate * duration))
    y1 = amp1 * np.sin(2 * np.pi * freq1 * x + phase1)
    y2 = amp2 * np.sin(2 * np.pi * freq2 * x + phase2)

    _, ax = plt.subplots()
    ax.plot(x, y1)
    ax.plot(x, y2)
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Amplitude')
    ax.set_title('Two sine waves')
    ax.grid(True)
    # plt.show()
    my_stringIObytes = BytesIO()
    plt.savefig(my_stringIObytes, format='jpg')
    my_stringIObytes.seek(0)
    return base64.b64encode(my_stringIObytes.read()).decode()


if __name__ == "__main__":
    print(myplot(1, 1, 1, 2, 0, 0))
