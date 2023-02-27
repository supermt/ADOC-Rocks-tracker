
    # # fig.add_shape(type='line',x0='400mb',y0=0,x1='400mb',y1=300000,
    # #         line=dict(color='LightSeaGreen',width=4,dash='dot'))
    # fig.update_layout(
    #     shapes=[
    #         # 1st highlight during Feb 4 - Feb 6
    #         dict(
    #             type="rect",
    #             xref="paper",
    #             yref="paper",
    #             x0=0,
    #             y0=0,
    #             x1=0.25,
    #             y1=1,
    #             fillcolor="LightSeaGreen",
    #             opacity=0.5,
    #             layer="below",
    #             line_width=0,
    #         ),
    #         dict(
    #             type="rect",
    #             xref="paper",
    #             yref="paper",
    #             x0=0.25,
    #             y0=0,
    #             x1=0.5,
    #             y1=1,
    #             fillcolor="Red",
    #             opacity=0.5,
    #             layer="below",
    #             line_width=0,
    #         ),
    #         dict(
    #             type="rect",
    #             xref="paper",
    #             yref="paper",
    #             x0=0.5,
    #             y0=0,
    #             x1=0.75,
    #             y1=1,
    #             fillcolor="Blue",
    #             opacity=0.5,
    #             layer="below",
    #             line_width=0,
    #         ),
    #         # 2nd highlight during Feb 20 - Feb 23
    #         # dict(
    #         #     type="rect",
    #         #     xref="x",
    #         #     yref="paper",
    #         #     x0="600mb",
    #         #     y0=0,
    #         #     x1="1200mb",
    #         #     y1=300000,
    #         #     fillcolor="LightSeaGreen",
    #         #     opacity=0.5,
    #         #     layer="below",
    #         #     line_width=0,
    #         # )
    #     ]
    # )
    # fig.update_layout(
    #     margin=dict(l=10, r=10, t=10, b=10),
    #     paper_bgcolor="LightSteelBlue",
    #     yaxis=dict(title="IOPS"),
    #     xaxis=dict(title="Bandwidth (MB/s)"),
    #     font=dict(size=20)
    # )